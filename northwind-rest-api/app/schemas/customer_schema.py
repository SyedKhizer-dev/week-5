from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):

    company: str | None = Field(default=None, max_length=50)

    first_name: str | None = Field(default=None, max_length=50)

    last_name: str | None = Field(default=None, max_length=50)

    email_address: str | None = Field(default=None, max_length=50)

    job_title: str | None = Field(default=None, max_length=50)

    business_phone: str | None = Field(default=None, max_length=25)

    city: str | None = Field(default=None, max_length=50)

    country_region: str | None = Field(default=None, max_length=50)


class CustomerUpdate(BaseModel):

    company: str | None = Field(default=None, max_length=50)

    first_name: str | None = Field(default=None, max_length=50)

    last_name: str | None = Field(default=None, max_length=50)

    email_address: str | None = Field(default=None, max_length=50)

    job_title: str | None = Field(default=None, max_length=50)

    business_phone: str | None = Field(default=None, max_length=25)

    city: str | None = Field(default=None, max_length=50)

    country_region: str | None = Field(default=None, max_length=50)


class CustomerResponse(BaseModel):

    id: int

    company: str | None

    first_name: str | None

    last_name: str | None

    email_address: str | None

    job_title: str | None

    business_phone: str | None

    city: str | None

    country_region: str | None

    model_config = ConfigDict(from_attributes=True)
