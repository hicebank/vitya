# vitya

**WARNING**: This library is still in development stage.

Validators for different russian banking values.  
Values you can validate:
- ИНН ```validate_inn```
- КПП ```validate_kpp```
- БИК ```validate_bic```
- ОГРН ```validate_ogrn```

You should pass value as ```str```, otherwise exception will be raised.  
If passed value is wrong, all functions will raise ```ValidationError```.


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
```