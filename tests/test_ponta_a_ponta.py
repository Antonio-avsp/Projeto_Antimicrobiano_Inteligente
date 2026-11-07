"""Teste ponta a ponta do fluxo principal do PGA, pela API e com login real de cada perfil.

Catálogo → prescrição → painel → cultura com antibiograma → reavaliação → encerramento →
nova terapia → relatórios. Cobre os casos de uso UC01 a UC08 em sequência.
"""

from datetime import date, timedelta

HOJE = date.today()


def dia(n: int) -> str:
    return (HOJE - timedelta(days=n)).isoformat()


def test_fluxo_principal_do_pga(client):
    # UC08 — o GESTOR cadastra a equipe; cada um entra com login e senha.
    equipe = {
        "farmaceutico": "FARMACEUTICO",
        "infectologista": "INFECTOLOGISTA",
        "laboratorio": "LABORATORIO",
    }
    tokens = {}
    for login, perfil in equipe.items():
        cadastro = client.post(
            "/usuarios",
            json={"login": login, "nome": login.title(), "perfil": perfil, "senha": "senha-e2e-1"},
        )
        assert cadastro.status_code == 201, cadastro.text
        entrada = client.post("/auth/login", json={"login": login, "senha": "senha-e2e-1"})
        assert entrada.status_code == 200, entrada.text
        tokens[login] = {"Authorization": f"Bearer {entrada.json()['access_token']}"}
    farmacia, infecto, lab = tokens["farmaceutico"], tokens["infectologista"], tokens["laboratorio"]

    # UC01 — o farmacêutico monta o catálogo.
    catalogo = {}
    for nome, classe, categoria, restrito in [
        ("Ceftriaxona", "Cefalosporina de 3ª geração", "WATCH", False),
        ("Meropenem", "Carbapenêmico", "WATCH", True),
        ("Gentamicina", "Aminoglicosídeo", "ACCESS", False),
    ]:
        resposta = client.post(
            "/antimicrobianos",
            json={
                "nome": nome,
                "classe": classe,
                "categoria_aware": categoria,
                "uso_restrito": restrito,
            },
            headers=farmacia,
        )
        assert resposta.status_code == 201, resposta.text
        catalogo[nome] = resposta.json()["id"]

    # UC02 — o infectologista prescreve terapia empírica há 4 dias, sem cultura.
    prescricao = client.post(
        "/prescricoes",
        json={
            "paciente_codigo": "PAC-0100",
            "setor": "UTI Adulto",
            "antimicrobiano_id": catalogo["Ceftriaxona"],
            "dose": "2 g",
            "intervalo_horas": 24,
            "via": "IV",
            "indicacao": "EMPIRICA",
            "diagnostico": "Pneumonia associada à ventilação",
            "data_inicio": dia(4),
            "duracao_prevista_dias": 7,
        },
        headers=infecto,
    )
    assert prescricao.status_code == 201, prescricao.text
    prescricao = prescricao.json()
    assert (prescricao["dia_de_terapia"], prescricao["registrado_por"]) == (5, "infectologista")

    # UC05 — o painel aponta o time-out e a falta de cultura.
    def tipos_do_paciente() -> set[str]:
        painel = client.get("/alertas", params={"paciente_codigo": "PAC-0100"}, headers=farmacia)
        assert painel.status_code == 200, painel.text
        return {alerta["tipo"] for alerta in painel.json()["alertas"]}

    assert tipos_do_paciente() == {"TIMEOUT_REAVALIACAO", "SEM_CULTURA"}

    # UC04 — o laboratório registra a cultura coletada no início e o antibiograma.
    cultura = client.post(
        "/culturas",
        json={
            "paciente_codigo": "PAC-0100",
            "setor": "UTI Adulto",
            "material": "SECRECAO_TRAQUEAL",
            "data_coleta": dia(4),
        },
        headers=lab,
    )
    assert cultura.status_code == 201, cultura.text
    resultado = client.put(
        f"/culturas/{cultura.json()['id']}/resultado",
        json={
            "resultado": "POSITIVA",
            "microrganismo": "Klebsiella pneumoniae",
            "data_resultado": dia(1),
            "antibiograma": [
                {"antimicrobiano_id": catalogo["Ceftriaxona"], "interpretacao": "R"},
                {"antimicrobiano_id": catalogo["Meropenem"], "interpretacao": "S"},
                {"antimicrobiano_id": catalogo["Gentamicina"], "interpretacao": "S"},
            ],
        },
        headers=lab,
    )
    assert resultado.status_code == 200, resultado.text

    # A cultura resolve a falta de cultura e revela a resistência, sugerindo ACCESS primeiro.
    painel = client.get("/alertas", params={"tipo": "RESISTENCIA"}, headers=farmacia).json()
    assert tipos_do_paciente() == {"TIMEOUT_REAVALIACAO", "RESISTENCIA"}
    recomendacao = painel["alertas"][0]["recomendacao"]
    assert recomendacao.index("Gentamicina") < recomendacao.index("Meropenem")

    # UC03 — o infectologista reavalia, suspende a ceftriaxona e inicia a gentamicina.
    reavaliacao = client.post(
        f"/prescricoes/{prescricao['id']}/reavaliacoes",
        json={"conduta": "AJUSTAR", "observacao": "Trocar conforme antibiograma"},
        headers=infecto,
    )
    assert reavaliacao.status_code == 201, reavaliacao.text
    encerrada = client.post(
        f"/prescricoes/{prescricao['id']}/encerramento",
        json={"status_final": "SUSPENSA", "motivo": "Microrganismo resistente"},
        headers=infecto,
    )
    assert encerrada.json()["status"] == "SUSPENSA"
    assert encerrada.json()["encerrado_por"] == "infectologista"
    nova = client.post(
        "/prescricoes",
        json={
            "paciente_codigo": "PAC-0100",
            "setor": "UTI Adulto",
            "antimicrobiano_id": catalogo["Gentamicina"],
            "dose": "5 mg/kg",
            "intervalo_horas": 24,
            "via": "IV",
            "indicacao": "DIRIGIDA",
            "diagnostico": "Pneumonia associada à ventilação",
            "data_inicio": dia(0),
            "duracao_prevista_dias": 7,
        },
        headers=infecto,
    )
    assert nova.status_code == 201, nova.text

    # Estado final esperado: nenhum alerta pendente para o paciente.
    assert tipos_do_paciente() == set()
    bloqueada = client.patch(
        f"/prescricoes/{prescricao['id']}", json={"dose": "1 g"}, headers=infecto
    )
    assert bloqueada.status_code == 409

    # UC06 e UC07 — relatórios de microbiologia e de consumo.
    antibiograma = client.get(
        "/relatorios/antibiograma-cumulativo",
        params={"inicio": dia(30), "fim": dia(0)},
        headers=farmacia,
    ).json()
    assert antibiograma["total_isolados"] == 1
    consumo = client.get(
        "/relatorios/indicadores", params={"inicio": dia(30), "fim": dia(0)}, headers=farmacia
    ).json()
    dot = {linha["antimicrobiano"]: linha["dot"] for linha in consumo["por_antimicrobiano"]}
    assert dot == {"Ceftriaxona": 5, "Gentamicina": 1}
    assert consumo["percentual_access"] == 16.7

    # Permissões ao longo do fluxo: o laboratório não prescreve.
    negado = client.post("/prescricoes", json=nova.json() | {"antimicrobiano_id": 1}, headers=lab)
    assert negado.status_code == 403
