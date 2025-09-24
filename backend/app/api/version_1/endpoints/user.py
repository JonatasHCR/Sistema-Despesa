from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.service.user import UserService
from app.schema.user import UserSchema, UserOutputSchema
from app.api.version_1.endpoints.base import BaseEndpoint


class UserEndpoint(BaseEndpoint[UserService, UserSchema, UserOutputSchema]):
    def __init__(self):
        super().__init__(
            prefix="/users",
            service=UserService,
            output_schema=UserOutputSchema,
            input_schema=UserSchema,
            tags=["User"],
        )
        super()._register_routes()
        self.register_routes()

    def register_routes(self):
        self.router.get("/email/{email}", response_model=UserOutputSchema)(
            self.get_by_email
        )

    async def get_by_email(
        self, email: str, db: AsyncSession = Depends(get_db)
    ) -> UserOutputSchema:
        service = self.service(db)
        try:
            return await service.get_by_email(email)
        except ValueError as error:
            raise HTTPException(status_code=404, detail=str(error))