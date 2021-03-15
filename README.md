# vitya

**WARNING**: This library is still in development stage.

Validators for different russian banking values.  
Values you can validate:
- ИНН ```validate_inn```
    - ИНН для ИП/Физ.Лица ```validate_inn_ip```
    - ИНН для Юр.Лица ```validate_inn_jur```
- КПП ```validate_kpp```
- БИК ```validate_bic```
- ОГРН ```validate_ogrn```
    - ОГРНИП ```validate_ogrnip```
- СНИЛС ```validate_snils```

You should pass value as ```str```, otherwise exception will be raised.  
If passed value is wrong, all functions will raise ```ValidationError```.

Also, optionally, you can use validators as Pydantic fields

### Examples:

```python
validate_inn("3664069397")

try:
    validate_inn("770708389")
except ValidationError as e:
    print(f"wrong inn: {e}")
```

```python
validate_kpp("616401001")
validate_bic("044525901")
validate_ogrn("1027700132195")
validate_snils("11223344595")
```

```python
from pydantic import BaseModel, ValidationError
from vitya.pydantic_fields import Inn


class InnModel(BaseModel):
    inn: Inn


inn_model = InnModel(inn="302502032671")
assert inn_model.inn == "302502032671"    

try:
    InnModel(inn="3664069398")
except ValidationError as e:
    print(e.errors())
```