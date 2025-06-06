from prisma.models import Users as PrismaUsers
from prisma.errors import UniqueViolationError

def create_user_in_db(user_data):
    try:
        response = PrismaUsers.prisma().create(data=user_data)
        return response.dict(), None
    except UniqueViolationError as error_msg:
        return None, str(error_msg)
    except Exception as e:
        return None, str(e)


def find_user_by_email_or_username(email=None, username=None):
    if email:
        return PrismaUsers.prisma().find_first(where={"email": email})
    return PrismaUsers.prisma().find_first(where={"username": username}) 