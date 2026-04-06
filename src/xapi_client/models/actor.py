from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class Account(BaseModel):
    home_page: str = Field(alias="homePage")
    name: str

    model_config = {"populate_by_name": True}


class Actor(BaseModel):
    object_type: str = Field(default="Agent", alias="objectType")
    name: str | None = None
    mbox: str | None = None
    mbox_sha1sum: str | None = None
    openid: str | None = None
    account: Account | None = None
    member: list[Actor] | None = None

    model_config = {"populate_by_name": True}

    @model_validator(mode="after")
    def _check_identifier(self):
        # anonymous groups don't need an inverse functional identifier
        if self.object_type == "Group" and self.member is not None:
            return self

        ids = [self.mbox, self.mbox_sha1sum, self.openid, self.account]
        count = sum(1 for x in ids if x is not None)
        if count != 1:
            raise ValueError(
                "Actor requires exactly one inverse functional identifier "
                "(mbox, mbox_sha1sum, openid, or account)"
            )
        return self

    @classmethod
    def from_email(cls, email: str, name: str | None = None) -> Actor:
        mailto = email if email.startswith("mailto:") else f"mailto:{email}"
        return cls(mbox=mailto, name=name)

    @classmethod
    def from_account(
        cls, home_page: str, account_name: str, name: str | None = None
    ) -> Actor:
        return cls(
            account=Account(home_page=home_page, name=account_name), name=name
        )
