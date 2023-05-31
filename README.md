# vitya

**WARNING**: This library is still in development stage.

Validators for different russian banking values.  
Values you can validate:
- ИНН ```validate_inn```
    - ИНН для ИП/Физ.Лица ```validate_inn_ip```
    - ИНН для Юр.Лица ```validate_inn_le```
- КПП ```validate_kpp```
- БИК ```validate_bic```
- ОГРН ```validate_ogrn```
    - ОГРНИП ```validate_ogrnip```
- СНИЛС ```validate_snils```
- ОКТМО ```validate_oktmo```

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
validate_oktmo("69701000001")
```

```python
from pydantic import BaseModel, ValidationError
from vitya.pydantic_fields import INN


class InnModel(BaseModel):
    inn: INN


inn_model = InnModel(inn="302502032671")
assert inn_model.inn == "302502032671"

try:
    InnModel(inn="3664069398")
except ValidationError as e:
    print(e.errors())
```

# Валидация платежей по реквизитам (Russian)
Для валидации платежей используется следующий базовый класс, 
от которого необходимо наследоваться:  

```python
class BaseModelChecker
````

У наследников этого класса есть переменная класса:  
```python
__checkers__: ClassVar[List[Tuple[Type[BaseChecker], List[str]]]] = []
````

В этой переменной содержится список чекеров (наследников BaseChecker),
которые будут вызваны (вызовется метод check) 
при инициализации инстансов BaseModelChecker  

Класс чекеров наследуется от BaseChecker
```python
class BaseChecker(ABC):
    @abstractmethod
    def check(self) -> None:  # pragma: no cover
        pass
```  


При инициализации инстансов класса BaseModelChecker, когда появляется проверка 
чекеров не выполняется успешно, выбрасывается ошибка CheckerError, 
которая затем оборачивается в pydantic.ValidationError
```python
class CheckerError(ValueError):
    def __init__(self, errors: Sequence[Exception]):
        self._errors = errors

    @property
    def errors(self) -> Sequence[Exception]:
        return self._errors
```

### Пример работы
Для примера разберем базовую ситуацию: ключевание номера счёта и БИКа банка. 
Чтобы это проверить, нам нужно создать класс наследник BaseModelChecker, 
со встроенным чекером ключевания счёта и БИКа. 
Такой чекер есть в базовых реализациях и называется AccountBicChecker. 

Пример кода:
```python
class MyPayment(BaseModelChecker):
    account_number: AccountNumber
    bic: BIC

    __checkers__ = [
        (AccountBicChecker, ['account_number', 'bic'])
    ]

try:
    payment = MyPayment(account_number='40802810722200035222', bic='045004861')
except ValidationError as e:
    print('ой, что-то не так с данными: ', str(e))
else:
    print('все отлично!')
```

Результат выполнения:
```
ой, что-то не так с данными:  1 validation error for TestAccountBicModelChecker
__root__
  [AccountValidationBICValueError()] (type=value_error.checker; _errors=[AccountValidationBICValueError()])
```

Поменяем БИК на корректный (последнюю цифру)
```python
try:
    payment = MyPayment(account_number='40802810722200035222', bic='045004864')
except ValidationError as e:
    print('ой, что-то не так с данными: ', str(e))
else:
    print('все отлично!')
```
Результат выполнения:
```
все отлично!
```