from enum import Enum

#========== Models Enum ===============

class UserRoleEnum(str,Enum):
    user = "User"
    admin = "Admin"
    super_admin = "Super Admin"


class PlanEnum(str, Enum):
    basic = "Basic"
    advance = "Advance"
    expert = "Expert"
    company = "Company"


class Genero(str, Enum):
    masculino = "Homme"
    femenino = "Femme"
    otro = "Autre"