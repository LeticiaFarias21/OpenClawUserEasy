# Sistema Multiagente: Processo Judicial Brasileiro — Primeira Instância

## Metadados do Sistema

```yaml
system_name: processo_judicial_br_1a_instancia
version: "1.0"
framework: OpenCLAWN
domain: judicial_brasil
base_legal: CPC/2015 (Lei nº 13.105/2015) | CPP (Decreto-Lei nº 3.689/1941) | CF/1988
```

---

## Agentes Registrados

| ID | Arquivo | Nome | Função Principal |
|----|---------|------|-----------------|
| `magistrado` | `agente_magistrado.md` | Magistrado — Gabinete | Direção do processo e prolação de pronunciamentos judiciais |
| `secretaria` | `agente_secretaria.md` | Secretaria Judicial | Fluxo cartorário, atos ordinatórios, expedição |
| `oficial_justica` | `agente_oficial_justica.md` | Oficial de Justiça | Execução material das ordens judiciais em campo |
| `perito_judicial` | `agente_perito_judicial.md` | Perito Judicial | Prova técnica especializada, laudo pericial |
| `ministerio_publico` | `agente_ministerio_publico.md` | Ministério Público | Ação penal (órgão agente) e fiscal da ordem jurídica |
| `partes` | `agente_partes.md` | Partes e Representantes | Postulação, contestação, reconvenção, recursos |

---

## Fluxo de Interação entre Agentes

```
[partes] ──petição inicial──► [secretaria] ──distribui e autua──► [magistrado]
                                                                        │
                        ┌───────────────────────────────────────────────┘
                        │ controle de admissibilidade
                        ▼
              ┌─── emenda da inicial?
              │         │
           [partes]◄────┘  (ordinatório da Secretaria)
              │
              └─── OK? → [secretaria] ──expede mandado──► [oficial_justica]
                                                                    │
                                                           citação/diligência
                                                                    │
                                              certidão de devolução ▼
                                          [secretaria] ──publica DJE──► [partes/réu]
                                                                              │
                                                               ┌──────────────┘
                                                               │ contestação (15 dias)
                                                               ▼
                                                          [secretaria]
                                                               │
                                          ┌────────────────────┴─────────────────────┐
                                          │                                           │
                          verificar art.178 CPC?                             concluso ao magistrado
                                          │                                           │
                                     [mp] ◄───vista──[secretaria]          [magistrado] saneamento
                                          │                                           │
                                     parecer                              ┌───────────┴───────────┐
                                          │                               │                       │
                                          ▼                       julgamento                instrução
                                    [magistrado]                  antecipado             probatória
                                          │                           │                       │
                                     sentença                    sentença               [perito_judicial]
                                          │                                                    │
                               [secretaria] executa                                       laudo
                                          │                                                    │
                              mandados [oficial_justica]                          [partes] assistentes
                                                                                              │
                                                                                     [magistrado] AIJ
                                                                                              │
                                                                                         sentença
```

---

## Regras de Roteamento Entre Agentes

```yaml
routing_rules:

  - trigger: "petição inicial protocolada"
    from: partes
    to: secretaria
    acao: autuação e distribuição

  - trigger: "processo autuado"
    from: secretaria
    to: magistrado
    acao: concluso para admissibilidade

  - trigger: "decisão de citação proferida"
    from: magistrado
    to: secretaria
    acao: expedição de mandado de citação

  - trigger: "mandado expedido"
    from: secretaria
    to: oficial_justica
    acao: carga do mandado na CEMAN

  - trigger: "certidão de devolução positiva"
    from: oficial_justica
    to: secretaria
    acao: juntada + intimação do réu para contestar

  - trigger: "certidão de devolução negativa"
    from: oficial_justica
    to: secretaria
    acao: intimar autor para novo endereço ou edital

  - trigger: "contestação protocolada"
    from: partes
    to: secretaria
    acao: juntada + ato ordinatório intimando autor para réplica

  - trigger: "réplica protocolada OU prazo expirado"
    from: secretaria
    to: secretaria
    acao: verificar art.178 CPC → abrir vista MP se necessário

  - trigger: "art.178 CPC configurado"
    from: secretaria
    to: ministerio_publico
    acao: vista dos autos para parecer (30 dias)

  - trigger: "parecer do MP juntado OU intervenção dispensada"
    from: secretaria
    to: magistrado
    acao: concluso para saneamento ou julgamento

  - trigger: "decisão de saneamento com prova pericial"
    from: magistrado
    to: secretaria
    acao: intimar perito + partes (15 dias para quesitos e indicação de assistente)

  - trigger: "laudo pericial juntado"
    from: perito_judicial
    to: secretaria
    acao: intimar partes (15 dias para manifestação sobre o laudo)

  - trigger: "instrução encerrada"
    from: secretaria
    to: magistrado
    acao: concluso para julgamento (AIJ ou sentença)

  - trigger: "sentença prolatada"
    from: magistrado
    to: secretaria
    acao: publicação, intimação das partes, início da fase de cumprimento/recursal
```

---

## Alertas de Sistema (Cross-Agent)

```yaml
system_alerts:

  - id: NULIDADE_MP_NAO_INTIMADO
    severity: CRITICO
    condicao: processo.hipotese_art178 == true AND ministerio_publico.manifestou == false AND status == "prestes a sentença"
    acao: BLOQUEAR fluxo — forçar intervenção do MP antes da sentença
    agente_responsavel: secretaria

  - id: PRAZO_PRESO_EXPIRADO
    severity: CRITICO
    condicao: indiciado_preso == true AND dias_sem_manifestacao_mp >= 5
    acao: ALERTAR magistrado — possível constrangimento ilegal
    agente_responsavel: magistrado

  - id: LAUDO_OMISSO_BLOQUEANTE
    severity: ALTO
    condicao: laudo.quesitos_sem_resposta.count > 0
    acao: Magistrado intima perito para complementação com prazo e pena
    agente_responsavel: magistrado

  - id: MANDADO_MOROSO
    severity: MEDIO
    condicao: mandado.prazo_retorno < data_atual AND mandado.status == "Com o Oficial"
    acao: Secretaria alerta magistrado sobre mora do Oficial
    agente_responsavel: secretaria
```

---

## Instâncias de Implantação

```yaml
deployment:
  sistema_pje: true
  sistema_esaj: true
  sistema_eproc: true
  sistema_projudi: true
  integracao_ceman: true       # Central de Mandados
  integracao_dje: true         # Diário de Justiça Eletrônico
  integracao_sisbajud: true    # Bloqueio de ativos financeiros
  integracao_renajud: true     # Constrição de veículos
  integracao_infojud: true     # Informações fiscais/patrimoniais
```

---

## Estrutura de Arquivos

```
agentes_judiciais/
├── 00_orquestrador.md          ← este arquivo
├── agente_magistrado.md
├── agente_secretaria.md
├── agente_oficial_justica.md
├── agente_perito_judicial.md
├── agente_ministerio_publico.md
└── agente_partes.md
```
