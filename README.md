# TCFmock
TCF canada imtixoni uchun mock platforma

## Mockuplar

`Mockups/` papkasida saytning barcha oynalari bor (20 ta sahifa). Ro‘yxat va foydalanuvchi yo‘li `Mockups/index.html` da.
Har bir fayl to‘liq mustaqil: shrift, CSS va JS ichiga joylangan, ikki marta bosib ochiladi.

- Tillar: o‘zbekcha, ruscha, fransuzcha, inglizcha (admin panel hozircha faqat o‘zbekcha)
- Obuna: onlayn to‘lovsiz — admin foydalanuvchi yaratadi va tanga qo‘shadi, foydalanuvchi obunani o‘zi faollashtiradi
- Imtihon: CO (39 savol, 35 daqiqa) va CE (39 savol, 60 daqiqa); EE va EO keyinroq qo‘shiladi

### Tahrirlash

`Mockups/*.html` fayllari yig‘ib chiqariladi — ularni to‘g‘ridan-to‘g‘ri tahrirlamang. Manba:

```
Mockups/_src/
  pages/      sahifa tanasi (yuqorida front-matter: sarlavha, CSS, mockup nomi)
  partials/   takrorlanuvchi bo‘laklar: <!--#include nom-->
  i18n/       matnlar: uz.json, ru.json, fr.json, en.json (kalitlar bir xil bo‘lishi shart)
  assets/     base.css, admin.css, app.js, shrift va rasm
  build.py    yig‘uvchi
```

O‘zgartirgandan so‘ng:

```
python3 Mockups/_src/build.py
```

Matn qo‘shish: sahifada `<span data-i18n="kalit"></span>` yozing va kalitni to‘rttala JSON faylga qo‘shing.
Build kalitlar mos kelmasa xato beradi.
