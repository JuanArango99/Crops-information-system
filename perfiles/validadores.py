from django.contrib.auth.password_validation import MinimumLengthValidator, UserAttributeSimilarityValidator, CommonPasswordValidator,NumericPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.translation import ngettext
from django.core.exceptions import (
    FieldDoesNotExist,
    ImproperlyConfigured,
    ValidationError,
)
import re
from difflib import SequenceMatcher
from django.utils.translation import gettext as _


""" 
Se editan los validadores de contraseñas de Django para personalizar el texto 
y algunos parámetros como la longitud mínima de contraseña
"""

#Override al validador del numero minimo de caracteres.
class MinimumLengthValidator(MinimumLengthValidator):
    """
    Validate that the password is of a minimum length.
    """

    def __init__(self, min_length=5):
        self.min_length = min_length

    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                ngettext(
                    "La contraseña es muy corta, debe contener al menos "
                    "%(min_length)d caracter.",
                    "La contraseña es muy corta, debe contener al menos "
                    "%(min_length)d caracteres.",
                    self.min_length,
                ),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

    def get_help_text(self):
        return ngettext(
            "La contraseña debe contener al menos %(min_length)d caracter.",
            "La contraseña debe contener al menos %(min_length)d caracteres.",
            self.min_length,
        ) % {"min_length": self.min_length}

def exceeds_maximum_length_ratio(password, max_similarity, value):
    """
    Test that value is within a reasonable range of password.

    The following ratio calculations are based on testing SequenceMatcher like
    this:

    for i in range(0,6):
      print(10**i, SequenceMatcher(a='A', b='A'*(10**i)).quick_ratio())

    which yields:

    1 1.0
    10 0.18181818181818182
    100 0.019801980198019802
    1000 0.001998001998001998
    10000 0.00019998000199980003
    100000 1.999980000199998e-05

    This means a length_ratio of 10 should never yield a similarity higher than
    0.2, for 100 this is down to 0.02 and for 1000 it is 0.002. This can be
    calculated via 2 / length_ratio. As a result we avoid the potentially
    expensive sequence matching.
    """
    pwd_len = len(password)
    length_bound_similarity = max_similarity / 2 * pwd_len
    value_len = len(value)
    return pwd_len >= 10 * value_len and value_len < length_bound_similarity

class UserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    """
    Validate that the password is sufficiently different from the user's
    attributes.

    If no specific attributes are provided, look at a sensible list of
    defaults. Attributes that don't exist are ignored. Comparison is made to
    not only the full attribute value, but also its components, so that, for
    example, a password is validated against either part of an email address,
    as well as the full address.
    """

    def validate(self, password, user=None):
        if not user:
            return

        password = password.lower()
        for attribute_name in self.user_attributes:
            value = getattr(user, attribute_name, None)
            if not value or not isinstance(value, str):
                continue
            value_lower = value.lower()
            value_parts = re.split(r"\W+", value_lower) + [value_lower]
            for value_part in value_parts:
                if exceeds_maximum_length_ratio(
                    password, self.max_similarity, value_part
                ):
                    continue
                if (
                    SequenceMatcher(a=password, b=value_part).quick_ratio()
                    >= self.max_similarity
                ):
                    try:
                        verbose_name = str(
                            user._meta.get_field(attribute_name).verbose_name
                        )
                    except FieldDoesNotExist:
                        verbose_name = attribute_name
                    raise ValidationError(
                        _("La contraseña es similar a la información del usuario."),
                        code="password_too_similar",
                        params={"verbose_name": verbose_name},
                    )

    def get_help_text(self):
        return _(
            "La contraseña no puede ser similar a su información personal."
        )

class CommonPasswordValidator(CommonPasswordValidator):
    """
    Validate that the password is not a common password.

    The password is rejected if it occurs in a provided list of passwords,
    which may be gzipped. The list Django ships with contains 20000 common
    passwords (lowercased and deduplicated), created by Royce Williams:
    https://gist.github.com/roycewilliams/281ce539915a947a23db17137d91aeb7
    The password list must be lowercased to match the comparison in validate().
    """

    def validate(self, password, user=None):
        if password.lower().strip() in self.passwords:
            raise ValidationError(
                _("La contraseña es muy común."),
                code="password_too_common",
            )

    def get_help_text(self):
        return _("La contraseña no puede ser una usada comúnmente.")

class NumericPasswordValidator(NumericPasswordValidator):
    """
    Validate that the password is not entirely numeric.
    """

    def validate(self, password, user=None):
        if password.isdigit():
            raise ValidationError(
                _("La contraseña es enteramente numérica."),
                code="password_entirely_numeric",
            )

    def get_help_text(self):
        return _("La contraseña no puede ser solamente numérica.")