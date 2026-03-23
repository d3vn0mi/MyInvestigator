"""Email investigation module."""

from pni.modules.email.analyzer import EmailAnalyzer
from pni.modules.email.source import EmailLocalSource
from pni.modules.email.breach import EmailBreachSource
from pni.modules.email.social import EmailSocialSource

__all__ = ["EmailAnalyzer", "EmailLocalSource", "EmailBreachSource", "EmailSocialSource"]
