# 📊 Student Data Pipeline

مشروع **Data Pipeline لمعالجة بيانات الطلاب** باستخدام Python، يقوم باستخراج البيانات من عدة مصادر مختلفة، ثم دمجها وتنظيفها وتحويلها والتحقق من جودتها، وفي النهاية تخزين البيانات الصحيحة في **MongoDB**.

---

## 🎯 فكرة المشروع

الهدف من المشروع هو بناء Pipeline قادر على التعامل مع بيانات الطلاب القادمة من مصادر متعددة، وتحويلها إلى بيانات موحدة ونظيفة وجاهزة للتخزين والاستخدام.

المشروع يطبق مراحل عملية ETL:

```text
Extract
   ↓
Integrate
   ↓
Clean
   ↓
Transform
   ↓
Validate
   ↓
Load
   ↓
MongoDB
```

---

## 🗂️ مصادر البيانات

المشروع يستطيع التعامل مع عدة مصادر:

### 1. CSV

يتم قراءة بيانات الطلاب من ملف CSV موجود داخل:

```text
data/raw/students.csv
```

### 2. REST API

يستخرج بيانات الطلاب من API.

في بيئة الاختبار يتم استخدام API محلي:

```text
http://localhost:8000/students
```

### 3. SQLite Database

يتم استخراج بيانات إضافية من قاعدة بيانات SQLite الموجودة في:

```text
database/students.db
```

### 4. MongoDB كمصدر اختياري

يمكن للمشروع أيضًا قراءة بيانات إضافية من MongoDB كمصدر بيانات، ويمكن تفعيل أو تعطيل هذا المصدر من `config.json`.

### 5. Web Scraping

يحتوي المشروع على Web Scraper باستخدام:

* Python
* Requests
* BeautifulSoup
* Pandas

ويتم استخراج بيانات من جدول HTML.

في بيئة الاختبار يتم استخدام صفحة HTML محلية:

```text
http://localhost:8000/scraped-students
```

ومن البيانات التي يتم استخراجها:

```text
student_id
city
web_status
```

---

## 🔄 مراحل معالجة البيانات

### المرحلة الأولى: Extract

يتم استخراج البيانات من جميع المصادر المفعلة:

```text
CSV
API
SQLite
MongoDB (اختياري)
Web Scraping
```

---

### المرحلة الثانية: Integration

يتم دمج البيانات باستخدام:

```text
student_id
```

كمفتاح مشترك بين المصادر.

تم تصميم عملية الدمج بحيث تمنع:

* تكرار السجلات.
* زيادة عدد الصفوف بشكل غير مقصود.
* Cartesian Product.

---

### المرحلة الثالثة: Cleaning

يتم تنظيف البيانات من خلال:

* إزالة السجلات المكررة.
* معالجة القيم المفقودة.
* توحيد أنواع البيانات.
* توحيد النصوص.
* التعامل مع القيم غير الصالحة.

---

### المرحلة الرابعة: Transformation

يتم تطبيق عمليات التحويل المطلوبة على البيانات وتجهيزها بالشكل المناسب للمرحلة النهائية.

---

### المرحلة الخامسة: Validation

يتم التحقق من جودة البيانات قبل تخزينها.

يتم فصل:

```text
Valid Records
```

عن:

```text
Rejected Records
```

السجلات غير الصالحة لا يتم تخزينها في قاعدة البيانات النهائية.

ويتم حفظها في:

```text
data/rejected/rejected_records.csv
```

---

## 🗄️ تخزين البيانات النهائية

الوجهة النهائية للبيانات الصحيحة هي:

**MongoDB**

Database:

```text
student_pipeline
```

Collection:

```text
final_students
```

أي أن المسار النهائي هو:

```text
MongoDB
└── student_pipeline
    └── final_students
```

---

## 🔐 منع تكرار البيانات

يعتمد المشروع على:

```text
student_id
```

كمفتاح منطقي للطالب.

ويتم استخدام:

* Unique Index
* Upsert
* Bulk Write

لمنع إنشاء سجلات مكررة عند تشغيل الـPipeline أكثر من مرة.

---

## ⚙️ إعداد المشروع

يتم التحكم في مصادر البيانات وإعدادات MongoDB من خلال:

```text
config.json
```

مثال:

```json
{
    "output": {
        "mongodb": {
            "enabled": true,
            "uri": "mongodb://localhost:27017",
            "database": "student_pipeline",
            "collection": "final_students"
        }
    }
}
```

---

## 📁 هيكل المشروع

```text
student_data_pipeline/
│
├── app/
│   ├── output/
│   │   ├── csv_writer.py
│   │   └── mongodb_writer.py
│   │
│   ├── sources/
│   │   ├── api_source.py
│   │   ├── csv_source.py
│   │   ├── database_source.py
│   │   ├── mongodb.py
│   │   └── web_scraper.py
│   │
│   ├── transformation/
│   │   ├── cleaner.py
│   │   ├── integration.py
│   │   └── transformer.py
│   │
│   ├── validation/
│   │   └── quality.py
│   │
│   └── utils/
│       └── logger.py
│
├── data/
│   ├── raw/
│   └── rejected/
│
├── database/
│   └── students.db
│
├── mock_api/
│   ├── server.py
│   ├── students_api.json
│   └── students_scraped.html
│
├── tests/
│
├── config.json
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🛠️ التقنيات المستخدمة

| التقنية       | الاستخدام                        |
| ------------- | -------------------------------- |
| Python        | لغة البرمجة الأساسية             |
| Pandas        | معالجة وتحليل البيانات           |
| Requests      | الاتصال بالـAPI وجلب صفحات الويب |
| BeautifulSoup | استخراج البيانات من HTML         |
| SQLite        | مصدر بيانات                      |
| MongoDB       | تخزين البيانات النهائية          |
| PyMongo       | الاتصال بـMongoDB                |
| Pytest        | اختبار المشروع                   |
| Logging       | تسجيل مراحل تنفيذ الـPipeline    |
| JSON          | إعدادات المشروع والبيانات        |

---

## 📦 تثبيت المتطلبات

بعد تحميل المشروع، افتح Terminal داخل مجلد المشروع ثم نفذ:

```bash
pip install -r requirements.txt
```

---

## ▶️ تشغيل المشروع

أولًا تأكد من تشغيل MongoDB على جهازك.

ثم شغّل الـPipeline:

```bash
python main.py
```

المشروع سينفذ المراحل بالترتيب:

```text
Extract
↓
Integration
↓
Cleaning
↓
Transformation
↓
Validation
↓
MongoDB
```

---

## 🌐 تشغيل الـMock API والـWeb Scraping

لأغراض الاختبار، يمكن تشغيل السيرفر المحلي الموجود في:

```text
mock_api/server.py
```

ثم تشغيل:

```bash
python mock_api/server.py
```

وسيتم توفير مصادر الاختبار المحلية للـAPI وWeb Scraping.

---

## 🧪 تشغيل الاختبارات

لتشغيل اختبارات المشروع:

```bash
pytest
```

الاختبارات تغطي أجزاء مختلفة من المشروع، ومنها:

* Integration
* Validation
* Web Scraping
* MongoDB
* Logging
* Pipeline

---

## 🔎 التحقق من البيانات في MongoDB

بعد تشغيل المشروع، افتح **MongoDB Compass** واتصل بـ:

```text
mongodb://localhost:27017
```

ثم افتح:

```text
student_pipeline
    └── final_students
```

ستجد هناك البيانات النهائية التي اجتازت مرحلة الـValidation.

---

## 📌 ملاحظات مهمة

* بيانات MongoDB النهائية لا يتم حفظها في ملف CSV.
* ملف `rejected_records.csv` يحتوي على السجلات التي لم تجتز عملية التحقق.
* Web Scraping في بيئة المشروع الحالية يستخدم صفحة HTML محلية تجريبية بهدف اختبار وظيفة الـScraper.
* يمكن تغيير رابط الـScraping والـCSS Selectors من خلال `config.json`.
* يمكن تفعيل أو تعطيل مصادر البيانات المختلفة من خلال إعدادات المشروع.
* يجب عدم وضع كلمات المرور أو مفاتيح الاتصال السرية داخل الكود أو GitHub.

---

## 👩‍💻 الهدف التعليمي

تم بناء المشروع لتطبيق مفاهيم عملية في:

* Data Engineering
* ETL Pipelines
* Data Cleaning
* Data Integration
* Data Validation
* Web Scraping
* APIs
* Databases
* MongoDB
* Automated Testing

ويهدف إلى محاكاة طريقة بناء Data Pipeline متعددة المصادر بشكل منظم وقابل للتطوير.

---

## 📄 الترخيص

هذا المشروع تعليمي ويمكن استخدامه وتطويره لأغراض التعلم والتجربة.
