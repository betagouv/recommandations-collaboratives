from allauth.mfa.stages import AuthenticateStage


class RecocoMFAAuthenticateStage(AuthenticateStage):
    """Custom config for mfa"""

    def is_proconnect_login(self):
        sociallogin = (self.login.signal_kwargs or {}).get("sociallogin")
        return bool(
            sociallogin
            and sociallogin.account
            and sociallogin.account.provider == "proconnect"
        )

    def _should_handle(self, request) -> bool:
        if self.is_proconnect_login():
            return False
        return super()._should_handle(request)
