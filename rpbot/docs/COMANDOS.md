# 📖 Lista de Comandos — RPBOT

## 🎭 Personagem
| Comando | Descrição |
|---------|-----------|
| `?jogar` | Cria um novo personagem ou mostra seus personagens |
| `?personagens` | Lista todos os seus personagens |
| `?ativar <id>` | Ativa um personagem específico |
| `?perfil` | Mostra os dados do personagem ativo |

## 📊 Status
| Comando | Descrição |
|---------|-----------|
| `?status` | Mostra todos os status (saúde, energia, fome, etc) |
| `?saude` | Mostra apenas a saúde |
| `?energia` | Mostra apenas a energia |
| `?fome` | Mostra apenas a fome |
| `?felicidade` | Mostra apenas a felicidade |
| `?estresse` | Mostra apenas o estresse |
| `?higiene` | Mostra apenas a higiene |
| `?reputacao` | Mostra apenas a reputação |
| `?ficha` | Mostra a ficha criminal |
| `?objetivos [texto]` | Mostra ou define objetivos de vida |

## 💼 Profissões
| Comando | Descrição |
|---------|-----------|
| `?profissoes` | Lista todas as profissões disponíveis |
| `?escolherprofissao <nome>` | Escolhe uma profissão (ex: `?escolherprofissao motoboy`) |
| `?fazerprova <profissao>` | Faz prova para profissões com requisito |
| `?trabalhar` | Trabalha na profissão atual (com cooldown) |

## 🚨 Emergência
| Comando | Descrição |
|---------|-----------|
| `?acionar192 <descricao>` | Chama o SAMU (ex: `?acionar192 fui atropelado`) |
| `?acionar190 <descricao>` | Chama a Polícia (ex: `?acionar190 fui roubado`) |
| `?atender <id>` | Atende um chamado (só SAMU/PM) |

## 👨‍👩‍👧 Família
| Comando | Descrição |
|---------|-----------|
| `?familia` | Mostra seus familiares |
| `?adicionarfam <@user> <tipo>` | Convida alguém pra família (pai, mae, filho, filha, amigo) |
| `?aceitarfam <id>` | Aceita um convite de família |
| `?recusarfam <id>` | Recusa um convite de família |
| `?removerfam <@user> <tipo>` | Remove alguém da família |

## ⚖️ Justiça / OAB
| Comando | Descrição |
|---------|-----------|
| `?boletim <descricao>` | Registra um B.O. (vira texto formal via IA) |
| `?meusboletins` | Lista seus boletins |
| `?chamaroab <descricao>` | Abre um chamado jurídico |
| `?processar <@user> <tipo>` | Abre processo de remoção familiar |

## 💰 Economia
| Comando | Descrição |
|---------|-----------|
| `?saldo` | Mostra seu saldo |
| `?top` | Mostra os mais ricos |
| `?pagar <@user> <valor>` | Transfere dinheiro |

## 📋 Eventos
| Comando | Descrição |
|---------|-----------|
| `?eventos` | Mostra eventos ativos |
| `?tarefas` | Mostra tarefas diárias |

## ❓ Ajuda
| Comando | Descrição |
|---------|-----------|
| `?ajuda` | Mostra esta lista |
| `?ajuda <comando>` | Mostra detalhes de um comando específico |
