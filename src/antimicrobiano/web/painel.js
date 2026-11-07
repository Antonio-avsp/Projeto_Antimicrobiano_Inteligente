// Painel de alertas (RF18): login, filtros por setor e data, alertas agrupados por severidade.
"use strict";

const SEVERIDADES = [
  { valor: "ALTA", rotulo: "Alta", icone: "▲", descricao: "ação imediata" },
  { valor: "MEDIA", rotulo: "Média", icone: "●", descricao: "ação em até 24 horas" },
  { valor: "BAIXA", rotulo: "Baixa", icone: "▼", descricao: "oportunidade de otimização" },
];
const CHAVE_TOKEN = "ami-token";
const CHAVE_USUARIO = "ami-usuario";

const $ = (id) => document.getElementById(id);

function lerSessao(chave) {
  try { return sessionStorage.getItem(chave); } catch (e) { return null; }
}
function gravarSessao(chave, valor) {
  try {
    if (valor === null) sessionStorage.removeItem(chave); else sessionStorage.setItem(chave, valor);
  } catch (e) { /* armazenamento indisponível: a sessão dura até recarregar a página */ }
}

let token = lerSessao(CHAVE_TOKEN);

function elemento(tag, propriedades = {}, filhos = []) {
  const el = document.createElement(tag);
  Object.assign(el, propriedades);
  for (const filho of [].concat(filhos)) el.append(filho);
  return el;
}

function selo(severidade) {
  const info = SEVERIDADES.find((s) => s.valor === severidade);
  return elemento("span", { className: `selo ${severidade}`, textContent: `${info.icone} ${info.rotulo.toUpperCase()}` });
}

function mostrarErro(id, mensagem) {
  const el = $(id);
  el.textContent = mensagem || "";
  el.hidden = !mensagem;
}

async function chamarApi(caminho, opcoes = {}) {
  const resposta = await fetch(caminho, {
    ...opcoes,
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (resposta.status === 401 && caminho !== "/auth/login") {
    sair("Sua sessão expirou. Entre novamente.");
    throw new Error(corpo.mensagem || "Não autenticado.");
  }
  if (!resposta.ok) throw new Error(corpo.mensagem || `Erro ${resposta.status}.`);
  return corpo;
}

function mostrarTela(logado) {
  $("tela-login").hidden = logado;
  $("tela-painel").hidden = !logado;
  $("sessao").hidden = !logado;
  if (logado) $("usuario-logado").textContent = lerSessao(CHAVE_USUARIO) || "";
}

function sair(mensagem) {
  token = null;
  gravarSessao(CHAVE_TOKEN, null);
  gravarSessao(CHAVE_USUARIO, null);
  mostrarTela(false);
  mostrarErro("erro-login", mensagem);
}

function renderizarResumo(resumo) {
  $("resumo").replaceChildren(
    ...SEVERIDADES.map((s) =>
      elemento("li", { className: s.valor }, [
        selo(s.valor),
        elemento("strong", { textContent: String(resumo.por_severidade[s.valor] ?? 0) }),
        elemento("span", { className: "meta", textContent: s.descricao }),
      ])
    )
  );
}

function renderizarEvidencias(evidencias) {
  const lista = elemento("dl");
  for (const [chave, valor] of Object.entries(evidencias)) {
    let texto = String(valor);
    if (typeof valor === "boolean") texto = valor ? "sim" : "não";
    else if (Array.isArray(valor)) texto = valor.join(", ");
    else if (valor !== null && typeof valor === "object") texto = JSON.stringify(valor);
    lista.append(elemento("dt", { textContent: chave.replaceAll("_", " ") }), elemento("dd", { textContent: texto }));
  }
  return lista;
}

function renderizarAlerta(alerta) {
  const resumo = elemento("summary", {}, [
    elemento("span", { className: "linha" }, [
      selo(alerta.severidade),
      elemento("span", { className: "tipo", textContent: alerta.tipo }),
    ]),
    elemento("span", { textContent: alerta.mensagem }),
    elemento("span", {
      className: "meta",
      textContent: `${alerta.paciente_codigo} · ${alerta.setor} · ${alerta.antimicrobiano} · prescrição #${alerta.prescricao_id}`,
    }),
  ]);
  const detalhe = elemento("div", { className: "detalhe" }, [
    elemento("p", {}, [elemento("strong", { textContent: "Recomendação: " }), alerta.recomendacao]),
    elemento("p", { className: "meta", textContent: "Evidências usadas pela regra:" }),
    renderizarEvidencias(alerta.evidencias),
  ]);
  return elemento("details", { className: alerta.severidade }, [resumo, detalhe]);
}

function renderizarGrupos(alertas) {
  const grupos = $("grupos");
  if (!alertas.length) {
    grupos.replaceChildren(elemento("p", { className: "vazio", textContent: "Nenhum alerta para os filtros selecionados." }));
    return;
  }
  grupos.replaceChildren(
    ...SEVERIDADES.filter((s) => alertas.some((a) => a.severidade === s.valor)).map((s) => {
      const doGrupo = alertas.filter((a) => a.severidade === s.valor);
      return elemento("section", { className: `grupo ${s.valor}` }, [
        elemento("h2", {}, [selo(s.valor), `${doGrupo.length} alerta(s) — ${s.descricao}`]),
        ...doGrupo.map(renderizarAlerta),
      ]);
    })
  );
}

function atualizarSetores(alertas) {
  const select = $("setor");
  const atual = select.value;
  const setores = new Set([...select.options].map((o) => o.value).filter(Boolean));
  alertas.forEach((a) => setores.add(a.setor));
  select.replaceChildren(
    elemento("option", { value: "", textContent: "Todos os setores" }),
    ...[...setores].sort((a, b) => a.localeCompare(b, "pt-BR")).map((s) => elemento("option", { value: s, textContent: s }))
  );
  select.value = atual;
}

async function carregarPainel() {
  mostrarErro("erro-painel", "");
  const parametros = new URLSearchParams();
  if ($("setor").value) parametros.set("setor", $("setor").value);
  if ($("data-referencia").value) parametros.set("data_referencia", $("data-referencia").value);
  try {
    const painel = await chamarApi(`/alertas?${parametros}`);
    $("aviso").textContent = `${painel.aviso} Data de referência: ${painel.data_referencia}.`;
    renderizarResumo(painel.resumo);
    renderizarGrupos(painel.alertas);
    atualizarSetores(painel.alertas);
  } catch (erro) {
    if (token) mostrarErro("erro-painel", erro.message);
  }
}

$("form-login").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  mostrarErro("erro-login", "");
  try {
    const resposta = await chamarApi("/auth/login", {
      method: "POST",
      body: JSON.stringify({ login: $("login").value, senha: $("senha").value }),
    });
    token = resposta.access_token;
    gravarSessao(CHAVE_TOKEN, token);
    gravarSessao(CHAVE_USUARIO, `${resposta.usuario.nome} (${resposta.usuario.perfil})`);
    $("senha").value = "";
    mostrarTela(true);
    await carregarPainel();
  } catch (erro) {
    mostrarErro("erro-login", erro.message);
  }
});

$("filtros").addEventListener("submit", (evento) => {
  evento.preventDefault();
  carregarPainel();
});
$("sair").addEventListener("click", () => sair(""));

mostrarTela(Boolean(token));
if (token) carregarPainel();
