"""Decorator pra verificar se o usuário é admin do bot."""
from discord.ext import commands
from services.admin_service import eh_admin


def admin_only():
    """
    Decorator que verifica se o usuário é admin do bot.
    
    Uso:
        @commands.command(name="comando")
        @admin_only()
        async def meu_comando(self, ctx):
            ...
    """
    async def predicate(ctx):
        if not eh_admin(str(ctx.author.id)):
            # Mensagem genérica — não revela que existe sistema de admin
            raise commands.CheckFailure(
                "🚫 Você não tem permissão pra usar esse comando."
            )
        return True
    
    return commands.check(predicate)
