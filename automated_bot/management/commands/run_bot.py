from django.core.management.base import BaseCommand

from automated_bot.services import BotService


class Command(BaseCommand):
    help = 'Starts automated bot'

    def handle(self, *args, **kwargs):
        BotService().process()
