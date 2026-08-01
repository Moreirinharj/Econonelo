import discord
from discord.ext import commands

from data.constantes import COR_PADRAO, COR_INFO
from utils.embeds import embed_padrao, embed_info


class Ajuda(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ajuda", aliases=["help"])
    async def ajuda(self, ctx: commands.Context, comando: str = None):
        if comando is None:
            embed = embed_padrao("📖 Central de Ajuda", cor=COR_PADRAO)
            embed.add_field(name="📜 Herança", value="`?testamento` `?verherdeiros` `?heranca` `?receberheranca`", inline=False)
            embed.add_field(name="🆔 Identificação", value="`?meucpf` `?investigar`", inline=False)
            embed.add_field(name="🎭 Personagem", value="`?jogar` `?personagens` `?ativar` `?perfil` `?editar`", inline=False)
            embed.add_field(name="📊 Status", value="`?status` `?saude` `?energia` `?fome` `?felicidade` `?estresse` `?higiene` `?reputacao` `?ficha` `?objetivos`", inline=False)
            embed.add_field(name="💼 Profissões", value="`?profissoes` `?escolherprofissao` `?fazerprova` `?trabalhar` `?trabalharrapido` `?comandos` `?pedirdemissao`", inline=False)
            embed.add_field(name="🚨 Emergência", value="`?acionar192` `?acionar190` `?atender`", inline=False)
            embed.add_field(name="👨‍👩‍👧 Família", value="`?familia` `?adicionarfam` `?aceitarfam` `?removerfam`", inline=False)
            embed.add_field(name="⚖️ Justiça", value="`?boletim` `?meusboletins` `?chamaroab` `?processar` `?denunciar` `?processos` `?pagarfianca`", inline=False)
            embed.add_field(name="🏢 IA Empresas", value="`?statusempresa` `?rankingempresas` `?simularempresas`", inline=False)
            embed.add_field(name="🛵 Delivery", value="`?ifood` `?cardapio` `?pedir` `?meuspedidos` `?pedidospendentes` `?aceitarentrega` `?completarentrega`", inline=False)
            embed.add_field(name="🏢 Empresas/Trabalho", value="`?empresas` `?loja` `?comprar` `?vagas` `?candidatar`", inline=False)
            embed.add_field(name="💰 Economia", value="`?carteira` `?depositar` `?sacar` `?pixchave` `?pix` `?cartao` `?pagarcartao` `?extrato` `?top` `?pagar`", inline=False)
            embed.add_field(name="🎒 Inventário", value="`?inventario` `?daritem` `?usaritem` `?equipar` `?desequipar`", inline=False)
            embed.add_field(name="🏠 Casas", value="`?casas` `?minhascasas` `?comprarcasa` `?vendercasa` `?reformar` `?cofredepositar` `?cofresacar`", inline=False)
            embed.add_field(name="🚗 Veículos", value="`?veiculos` `?garagem` `?comprarveiculo` `?venderveiculo` `?abastecer` `?reparar` `?seguro`", inline=False)
            embed.add_field(name="🎓 Educação", value="`?universidades` `?vestibular` `?matricular` `?estudar` `?minhaseducacao` `?trancar` `?infouniversidade`", inline=False)
            embed.add_field(name="🌍 Mundo", value="`?mundo` `?noticias` `?locais` `?cidades` `?eventos`", inline=False)
            embed.add_field(name="👥 NPCs", value="`?npcs` `?npc` `?conversar` `?darnpc`", inline=False)
            embed.add_field(name="🕵️ Corrupção", value="`?subornar` `?aceitarsuborno` `?recusarsuborno` `?denunciarcorrupcao` `?historiocorrupcao`", inline=False)
            embed.add_field(name="🎮 Ações", value="`?comer` `?dormir` `?banho` `?relaxar` `?verificar`", inline=False)
            embed.add_field(name="🔑 Admin", value="`?ativaradmin` `?adminhelp`", inline=False)
            embed.add_field(name="🎮 Informações", value="`?news` `?menu` `?ajuda`", inline=False)
            embed.set_footer(text="Use ?ajuda <comando> pra detalhes de um comando específico.")
            await ctx.reply(embed=embed)
            return

        detalhes = {
            "jogar": ("🎭 ?jogar", "Cria um novo personagem ou mostra seus personagens existentes."),
            "meucpf": ("🆔 ?meucpf", "Mostra teu CPF sequencial (000-999)."),
            "agredir": ("⚔️ ?agredir <@user> [tipo]", "Agridi alguém (soco, chute, faca, arma_fogo, taco)."),
            "veracao": ("🔒 ?veracao <id>", "Vê detalhes de uma ação privada (só pra envolvidos)."),
            "defender": ("🛡️ ?defender <@user>", "Defende-se de quem te agrediu."),
            "curar": ("🏥 ?curar <@user>", "Médico/SAMU cura ferimentos."),
            "ferimento": ("🩹 ?ferimento [@user]", "Mostra nível de ferimento."),
            "tiposagressao": ("⚔️ ?tiposagressao", "Lista tipos de agressão e armas."),
            "comprararma": ("🔫 ?comprararma <nome>", "Compra arma no mercado negro."),
            "testamento": ("📜 ?testamento", "Cria, vê ou cancela teu testamento."),
            "verherdeiros": ("👥 ?verherdeiros", "Mostra quem seriam teus herdeiros legais."),
            "heranca": ("📦 ?heranca", "Mostra heranças pendentes pra você receber."),
            "receberheranca": ("💰 ?receberheranca <id>", "Recebe uma herança pendente."),
            "investigar": ("🔍 ?investigar <cpf>", "Investiga um CPF (só autoridades e médicos)."),
            "perfil": ("🎭 ?perfil", "Mostra o perfil completo do personagem ativo."),
            "editar": ("✏️ ?editar", "Edita campos pessoais do personagem (nome, idade, gênero, etc). Usa `?editar <campo> <valor>`."),
            "profissoes": ("💼 ?profissoes", "Lista todas as profissões disponíveis com requisitos."),
            "escolherprofissao": ("💼 ?escolherprofissao <nome>", "Escolhe sua profissão. Ex: `?escolherprofissao motoboy`"),
            "fazerprova": ("📝 ?fazerprova <profissao>", "Faz a prova para desbloquear profissões com requisito."),
            "trabalhar": ("💼 ?trabalhar", "Trabalha na sua profissão atual (minigame). Tem cooldown."),
            "trabalharrapido": ("💼 ?trabalharrapido", "Trabalho rápido sem minigame (50% da recompensa)."),
            "comandos": ("💼 ?comandos", "Mostra os comandos exclusivos da sua profissão atual."),
            "pedirdemissao": ("📤 ?pedirdemissao", "Pede demissão da profissão atual."),
            "acionar192": ("🚑 ?acionar192 <descricao>", "Chama o SAMU. Ex: `?acionar192 fui atropelado`"),
            "acionar190": ("🚓 ?acionar190 <descricao>", "Chama a Polícia. Ex: `?acionar190 fui roubado`"),
            "atender": ("🚨 ?atender <id>", "Atende um chamado de emergência (só SAMU/PM)."),
            "familia": ("👨‍👩‍👧 ?familia", "Mostra todos os seus familiares."),
            "adicionarfam": ("👨‍👩‍👧 ?adicionarfam <@user> <tipo>", "Convida alguém. Tipos: pai, mae, filho, filha, amigo."),
            "boletim": ("📝 ?boletim <descricao>", "Registra um B.O. A IA converte pra linguagem formal."),
            "denunciar": ("⚖️ ?denunciar <@user> <crime>", "Abre um processo judicial contra alguém."),
            "processos": ("⚖️ ?processos", "Lista processos judiciais em andamento."),
            "pagarfianca": ("⚖️ ?pagarfianca <id> <valor>", "Paga fiança de um processo."),
            "carteira": ("💰 ?carteira", "Mostra resumo financeiro completo (bolso, banco, cartão, PIX)."),
            "depositar": ("💰 ?depositar <valor>", "Deposita dinheiro do bolso no banco."),
            "sacar": ("💰 ?sacar <valor>", "Saca dinheiro do banco pro bolso."),
            "pixchave": ("🔑 ?pixchave <chave>", "Define sua chave PIX."),
            "pix": ("💸 ?pix <chave> <valor>", "Envia PIX pra outra pessoa pela chave."),
            "cartao": ("💳 ?cartao", "Mostra dados do cartão de crédito."),
            "pagarcartao": ("💳 ?pagarcartao <valor>", "Paga fatura do cartão usando saldo do banco."),
            "extrato": ("📜 ?extrato", "Mostra últimas transações financeiras."),
            "inventario": ("🎒 ?inventario", "Mostra inventário do personagem."),
            "casas": ("🏠 ?casas", "Lista casas à venda."),
            "minhascasas": ("🏠 ?minhascasas", "Mostra suas casas."),
            "comprarcasa": ("🏠 ?comprarcasa <id>", "Compra uma casa."),
            "veiculos": ("🚗 ?veiculos", "Lista veículos na concessionária."),
            "garagem": ("🚗 ?garagem", "Mostra seus veículos."),
            "universidades": ("🎓 ?universidades", "Lista cursos disponíveis."),
            "vestibular": ("🎓 ?vestibular <id>", "Faz vestibular pra um curso."),
            "ifood": ("🛵 ?ifood", "Mostra empresas disponíveis pra pedir delivery."),
            "statusempresa": ("🏢 ?statusempresa <id>", "Mostra status detalhado de uma empresa."),
            "rankingempresas": ("🏆 ?rankingempresas", "Mostra ranking das empresas por saldo."),
            "simularempresas": ("🏢 ?simularempresas", "Simula um dia das empresas (só admin)."),
            "cardapio": ("📋 ?cardapio <id_empresa>", "Mostra cardápio de uma empresa."),
            "pedir": ("🛵 ?pedir <id_empresa> <id_produto> [qtd]", "Faz um pedido de delivery."),
            "meuspedidos": ("📦 ?meuspedidos", "Mostra teus pedidos."),
            "pedidospendentes": ("🛵 ?pedidospendentes", "Mostra pedidos pendentes (só motoboys)."),
            "aceitarentrega": ("🛵 ?aceitarentrega <id>", "Motoboy aceita um pedido."),
            "completarentrega": ("✅ ?completarentrega <id>", "Motoboy completa uma entrega."),
            "infouniversidade": ("🏛️ ?infouniversidade [sigla]", "Mostra descrição, cursos e detalhes de uma universidade (ex: ?infouni usp)."),
            "matricular": ("🎓 ?matricular <id>", "Matricula no curso após aprovação."),
            "estudar": ("🎓 ?estudar", "Estuda um semestre do curso."),
            "mundo": ("🌍 ?mundo", "Mostra estado atual do mundo (dia, clima, inflação)."),
            "noticias": ("📰 ?noticias", "Mostra últimas notícias geradas pela IA."),
            "locais": ("📍 ?locais", "Lista locais do mundo."),
            "npcs": ("👥 ?npcs", "Lista NPCs."),
            "subornar": ("🕵️ ?subornar <@user> <valor>", "Tenta subornar alguém."),
            "aceitarsuborno": ("🕵️ ?aceitarsuborno <id>", "Aceita suborno pendente."),
            "recusarsuborno": ("🕵️ ?recusarsuborno <id>", "Recusa suborno e denuncia."),
            "denunciarcorrupcao": ("🕵️ ?denunciarcorrupcao <@user>", "Denuncia corrupção de alguém."),
            "comer": ("🍔 ?comer", "Come e recupera fome."),
            "dormir": ("💤 ?dormir [horas]", "Dorme e recupera energia."),
            "banho": ("🚿 ?banho", "Toma banho e recupera higiene."),
            "relaxar": ("😌 ?relaxar", "Relaxa e reduz estresse."),
        }

        chave = comando.lower().replace("?", "")
        if chave in detalhes:
            titulo, desc = detalhes[chave]
            await ctx.reply(embed=embed_info(titulo, desc))
        else:
            await ctx.reply(embed=embed_info("❓ Comando não encontrado", f"Use `?ajuda` pra ver a lista completa."))


async def setup(bot: commands.Bot):
    await bot.add_cog(Ajuda(bot))
