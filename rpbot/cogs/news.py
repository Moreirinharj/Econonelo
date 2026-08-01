import discord
from discord.ext import commands

from data.constantes import COR_PADRAO
from utils.embeds import embed_padrao


class News(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="news", aliases=["sobre", "features", "oquee", "porquejogar"])
    async def news_cmd(self, ctx: commands.Context):
        """
        Mostra por que jogar o bot e suas principais funcionalidades.
        """
        embed = embed_padrao(
            "🎮 Por que jogar Econonelo RP?",
            cor=COR_PADRAO
        )
        
        embed.description = (
            "**Econonelo RP** é um bot de RPG de vida real no Discord com imersão total!\n\n"
            "🌟 **Destaques:**\n"
            "• Sistema completo de vida real (trabalho, estudo, família, crimes)\n"
            "• Economia realista com banco, PIX, cartão de crédito\n"
            "• Profissões com minigames interativos\n"
            "• Universidades reais (USP, UFRJ, etc.) com cursos e vestibular\n"
            "• Empresas reais (McDonald's, Renner, Assaí) com delivery\n"
            "• Sistema de justiça completo (processos, corrupção, prisão)\n"
            "• Relacionamentos secretos e sistema de herança\n"
            "• Combate e agressão com consequências reais\n"
            "• Imersão geográfica (viagens entre estados, clima dinâmico)\n"
            "• E muito mais!\n\n"
            " **Comece agora:** `?jogar <seu_nome>`"
        )
        
        # Página 1: Personagem e Profissão
        embed.add_field(
            name=" Crie seu Personagem",
            value=(
                "• CPF único e identificação\n"
                "• Status completos (saúde, energia, fome, felicidade)\n"
                "• Inventário com itens e armas\n"
                "• Aparência personalizável\n"
                "• Histórico criminal e reputação"
            ),
            inline=True
        )
        
        embed.add_field(
            name="💼 Profissões e Carreira",
            value=(
                "• 15+ profissões disponíveis\n"
                "• Minigames interativos\n"
                "• Concursos públicos (PM, PC, Juiz, Médico)\n"
                "• Professores com especialidades\n"
                "• Salários e progressão de nível"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🎓 Educação",
            value=(
                "• Universidades reais (USP, UFRJ, UFMG...)\n"
                "• Vestibular com prova\n"
                "• 20+ cursos (Medicina, Direito, Engenharia...)\n"
                "• Aulas com professores\n"
                "• Diplomas e escolaridade"
            ),
            inline=True
        )
        
        # Página 2: Economia e Bens
        embed.add_field(
            name="💰 Economia Completa",
            value=(
                "• Banco com saldo e extrato\n"
                "• PIX com chave personalizada\n"
                "• Cartão de crédito com fatura\n"
                "• Transações e histórico\n"
                "• Ranking dos mais ricos"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🏠 Casas e Veículos",
            value=(
                "• Compre casas em diferentes cidades\n"
                "• Cofre seguro em cada casa\n"
                "• Garagem para veículos\n"
                "• Carros, motos com placa real\n"
                "• Abastecimento e reparos"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🛍️ Empresas Reais",
            value=(
                "• McDonald's, Burger King, Habib's\n"
                "• Assaí, Atacadão, Mix Mateus\n"
                "• Renner, Riachuelo, C&A\n"
                "• Drogasil, RaiaDrogasil\n"
                "• Compras com estoque real"
            ),
            inline=True
        )
        
        # Página 3: Imersão e Mundo
        embed.add_field(
            name=" Mundo Vivo",
            value=(
                "• 6 estados brasileiros (SP, RJ, MG, PR, RS, BA)\n"
                "• Viagens de avião entre estados\n"
                "• Clima dinâmico (chuva, calor, frio)\n"
                "• Estações do ano\n"
                "• Notícias geradas por IA"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🚨 Justiça e Crimes",
            value=(
                "• Sistema de B.O. e processos\n"
                "• Advogados e juízes\n"
                "• Corrupção e suborno\n"
                "• Prisão e fiança\n"
                "• Ficha criminal"
            ),
            inline=True
        )
        
        embed.add_field(
            name="⚔️ Combate",
            value=(
                "• Agressão com diferentes armas\n"
                "• Ferimentos e cura médica\n"
                "• Legítima defesa\n"
                "• Consequências reais (prisão, morte)\n"
                "• Ações privadas (só envolvidos veem)"
            ),
            inline=True
        )
        
        # Página 4: Social e Privacidade
        embed.add_field(
            name="👥 Vida Social",
            value=(
                "• Sistema de família (pais, filhos, cônjuges)\n"
                "• Relacionamentos secretos (amantes)\n"
                "• Sistema de traição e descoberta\n"
                "• NPCs interativos\n"
                "• Conversas e interações"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📜 Herança e Testamento",
            value=(
                "• Crie testamento com herdeiros\n"
                "• Herança legal (sem testamento)\n"
                "• Transferência de bens (casas, carros, dinheiro)\n"
                "• Imposto de herança (10%)\n"
                "• Sistema de morte com consequências"
            ),
            inline=True
        )
        
        embed.add_field(
            name=" Privacidade Total",
            value=(
                "• Ações sensíveis são privadas\n"
                "• Só envolvidos veem detalhes\n"
                "• Sem DMs invasivas\n"
                "• Mensagens efêmeras\n"
                "• Chat limpo e organizado"
            ),
            inline=True
        )
        
        # Footer com call-to-action
        embed.set_footer(
            text="💡 Comece sua jornada: ?jogar <seu nome> | 📋 Menu completo: ?menu"
        )
        
        await ctx.reply(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(News(bot))
