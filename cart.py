################################################
# Decision Tree Classification: CART
################################################

# 1. Exploratory Data Analysis
# 2. Data Preprocessing & Feature Engineering
# 3. Modeling using CART
# 4. Hyperparameter Optimization with GridSearchCV
# 5. Final Model
# 6. Feature Importance
# 7. Analyzing Model Complexity with Learning Curves (BONUS)
# 8. Visualizing the Decision Tree
# 9. Extracting Decision Rules
# 10. Extracting Python/SQL/Excel Codes of Decision Rules
# 11. Prediction using Python Codes
# 12. Saving and Loading Model


# pip install pydotplus
# pip install skompiler
# pip install astor
# pip install joblib

import warnings
import joblib
import pydotplus
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_graphviz, export_text
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split, GridSearchCV, cross_validate, validation_curve
from skompiler import skompile
import graphviz

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)

warnings.simplefilter(action='ignore', category=Warning)

################################################
# 1. Exploratory Data Analysis
################################################

################################################
# 2. Data Preprocessing & Feature Engineering
################################################

################################################
# 3. Modeling using CART
################################################

df = pd.read_csv("datasets/diabetes.csv") #veri setini çağırdık

y = df["Outcome"] #bağımlı değişkeni seçtik
X = df.drop(["Outcome"], axis=1) #bağımsız değişkeni seçtik

cart_model = DecisionTreeClassifier(random_state=1).fit(X, y)
#daha önceden import etiğimiz modelimizi çağırdık 
#değişkenlerimizi fit ettik
#random state hocayla aynı sonuçları alalım diye

# Confusion matrix için y_pred:
y_pred = cart_model.predict(X)
#tahmin edilen değerlerimiz bunlar sonra bunları değerlendiricez

# AUC için y_prob:
y_prob = cart_model.predict_proba(X)[:, 1]
#roc eğrisi için 1. sınıfa ait olma olasılıkları lazım bize
#auc hesaplıcaaz

# Confusion matrix
print(classification_report(y, y_pred))
#başarı değerimize bakıyoruz burada 1 çıktı mükemmel 1 atlayış
#precisionlar recall f1ler hep 1 maşallah

# AUC
roc_auc_score(y, y_prob)
#auc skor da 1 çıktı bu terste bir işlik yok mu

#overfit'e mi düştük yoksa
#başarımı nasıl daha doğru değerlendirebilirim diye holdout yöntemimiz var

#####################
# Holdout Yöntemi ile Başarı Değerlendirme
#####################

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=45)
# test ve train setlerimizi ikiye ayırdık train_test_split ile
#0.7'si train 0.3'ü test yaptık

#modelimizi kurduk yine 
cart_model = DecisionTreeClassifier(random_state=17).fit(X_train, y_train)

# Train Hatası
y_pred = cart_model.predict(X_train)
y_prob = cart_model.predict_proba(X_train)[:, 1]
print(classification_report(y_train, y_pred))
roc_auc_score(y_train, y_prob)
#train için bi baktık skorlarımız yine 1 geldi başarımız

# Test Hatası
y_pred = cart_model.predict(X_test)
y_prob = cart_model.predict_proba(X_test)[:, 1]
print(classification_report(y_test, y_pred))
roc_auc_score(y_test, y_prob)
#şimdi hiç görmediği test setinde gördük ki
#eğitildiği veride yüksek performans verdi ama
#görmediği veride precisionlar recall'lar f1'ler accuracy'ler hep düştü
#demek ki model göremediği veride berbar train set'ini ezberledi
#accuracy 0.71 fena değil ama kötü f1 0.58 çıktı biraz düşük ama kayde değer diyebiliriz

#random state'i değiştirip modeli yeniden kurduk baktık ki skorlar hep değişiyor
#işin içinden çıkamadık e napıcaz
#çapraz doğrulama selamın aleykum ben geliyorum diyecez 
#model başarımızı böyle değerlendiricez
#####################
# CV ile Başarı Değerlendirme
#####################

cart_model = DecisionTreeClassifier(random_state=17).fit(X, y)
#tamam aynı şekil modelimizi fit ettik
#şimdi cross validate yapıcaz kardeş ama yukarıda zaten sen tüm modeli fit ettin
#dersen eğer haklısın ama cross validate kardeş bu durumua ayarlıyor gerektiği gibi

cv_results = cross_validate(cart_model,
                            X, y,
                            cv=5,
                            scoring=["accuracy", "f1", "roc_auc"])

cv_results['test_accuracy'].mean()
# 0.7058568882098294
cv_results['test_f1'].mean()
# 0.5710621194523633
cv_results['test_roc_auc'].mean()
# 0.6719440950384347

#ŞİMDİ BİZ BURAYA KADAR NE YAPTIK KARDEŞ?
#E anlatayım; biz modelimizi kurduk bi baktık skorlarımız 1 geliyor
#dedik ki bu terste bir işlik var böyle olmaz ki ya 
#en iyisi  holdout yöntemiyle ben bi train test yapıyım dedik
#orada da işin içinden çıkamadık random state değiştikçe sonuçlar değişti
#aslında belki veri setimiz zengin olsa bu holdout yöntemi yeterli olurdu
#ama olmadı o yüzden cross validation yapalım dedik madem en sonunda
#en son artık elde ettiğimiz başarı oranları n doğru başarı oranlarıdır
#tamam en doğru sonuçları şimdi bulduk ama sonuçlar da biraz düşük kaldı gibi kardeş
#model başarımızı nasıl arttırırız şimdi?
#cvp: yeni değişkenler ekleyerek veri ön işleme yaparak ya da hiperparametre optimizasyonu yaparak 
#ek olarak bu veriseti özelinde dengesiz veri yaklaşımları da tercih edilebilir.

#biz bu seçeneklerden hiperparametere optimizasyonu seçmeke ve devamkee
################################################
# 4. Hyperparameter Optimization with GridSearchCV
################################################


cart_model.get_params()

#mevcut modelin hiperparametrelerini görmek için get_params kardeşi çağırdık
#biz buradaki çıktılardan en önemli olanları seçelimm
#mesela min_samples_split var ön tanımlı değeri de 2'ymiş
#yani iki tane kalana kadar bölme işlemine devam ediyor e bu overfit'e sebep olabilir 
#bi de max_depth var ön tanımlı değeri none bu da overfit yapıyordur muhtemelen

#şimdi denenecek olan parametre setleri için öntanımlı değerlerimizi verdik
cart_params = {'max_depth': range(1, 11),
               "min_samples_split": range(2, 20)}

#şimdi de gridsearchCV kardeşle bu parametrelere göre bi arama yapılmasını sağlayacağız
#ne diyordu bu kardeş? bana modeli göster hanhi hiperparametrelerde geziceğimi göster diyordu
#kaç katlı çapraz doğrulama ile hatalara bakıcağını gösterdik
#işlmciyi tam performans kullan dedik n_jobs=-1'le
#verbose true ile rapor ver kardeş dedik
cart_best_grid = GridSearchCV(cart_model,
                              cart_params,
                              cv=5,
                              n_jobs=-1,
                              verbose=1).fit(X, y)
#bu hiperparametre optm. tüm veriyle ya da train test ile de yapılabilir
#öneri tüm veri setiyle yapılmasından yana
#biz de veri seti boyutu az diye hepsini kullandık 
#sen istersen bunu train ile yapar sonra test ile test edebilirsin o da kayda değer bir yoldur

cart_best_grid.best_params_
#max depth: 5, min samples split:4 en iyi değerler bunlar çıktı

#o zaman şimdi en iy değerlere göre en iyi skorlarımıza bakalım
cart_best_grid.best_score_
#0.75 çıktı best score'da
#bu 0,75 ne? scoring ön tanımlı argüman var ön tanımlı değeri accuracy'dir
#bunu değiştirmeye gerek yok ama daha sonra gerekirse değiştirirsin
#f1 skor yaparsan bunu max depth ve min samples split değiştii
#dökümantasyon oku bol bol metodların detayına girr iyidir kardeşşş
#biz accuracy'de kaldık devam edicez

random = X.sample(1, random_state=45)

cart_best_grid.predict(random)


################################################
# 5. Final Model
################################################
#aha aşağıda modelimizi kurduk

cart_final = DecisionTreeClassifier(**cart_best_grid.best_params_, random_state=17).fit(X, y)
#şimdi bi parametrelerimize bakalım
cart_final.get_params()
#heh tamam gelmiş istediğimiz ön tanımlı değerlerimiz

#final model oluşturmanın bir yolu budur
#bir de bu var;
#en iyi parametreleri modele atamak için;
#bunu biye gösterdik bu parametreleri daha sonra metodsal fonksiyonel olarak atamamız gerekebilir
#napıyoruz böylece aşağıda: var olan bir modeli set_params'ı kullanarak final model yapabiliriz

cart_final = cart_model.set_params(**cart_best_grid.best_params_).fit(X, y)

#şimdi final modelimizin hata skorlarına  cross validate'lebakalım
cv_results = cross_validate(cart_final,
                            X, y,
                            cv=5,
                            scoring=["accuracy", "f1", "roc_auc"])

cv_results['test_accuracy'].mean()

cv_results['test_f1'].mean()

cv_results['test_roc_auc'].mean()
#evet yukarıdakilerin çıktılarından görecez ki ilerleme kaydettik


################################################
# 6. Feature Importance
################################################
#değişkenleri sahip olduğu önem sıralamasına göre sıralıcazke

cart_final.feature_importances_
#değişkenlerin önem özelliği yukarıdakini yapınca geldi ama format anlayabileceğimiz düzeyde değil
#o zaman öyle  bişey yapalım ki
#kıyamadığım serisinden fonksiyon aşağıdaaa!!!!!!
#önem sırasına göre sıralar, isimlerini verir ve bize görselleştirir bu çıktıı ooo

#burada ön tanımlı argüman num var değişken kadarınca dedik biz ilk 5'de diyebilirdik duruma göre
#ilk argümanımız da model
#3. argüman değişkenler, feature'lar, kolonlar
#save diye bi argüman var false dedik true dersek kaydeder bak aşağıda sonda if save: plt.save bişeyler var
def plot_importance(model, features, num=len(X), save=False):
    feature_imp = pd.DataFrame({'Value': model.feature_importances_, 'Feature': features.columns})
    plt.figure(figsize=(10, 10))
    sns.set(font_scale=1)
    sns.barplot(x="Value", y="Feature", data=feature_imp.sort_values(by="Value",
                                                                     ascending=False)[0:num])
    plt.title('Features')
    plt.tight_layout()
    plt.show()
    if save:
        plt.savefig('importances.png')


plot_importance(cart_final, X, num=5)

################################################
# 7. Analyzing Model Complexity with Learning Curves (BONUS)
################################################

#overfit'e düştüm mü sorusunun cevabı train ve test setinin farklarının ayrışmaya
#başladığı noktadır dedik kardeş..
#nasıl yakalarım bunu ayrıştığı noktaya bakarız
#önüne geçmek için model karmaşıklığı azaltırız böylece önüne geçeriz
#model karmaşıklığı metrikleri modellere göre değişir 
#yani başka modelde başka hiperparametreler model karmaşıklığı metrikleridir
#şimdi validation curve diye metodumuz var 
#diyor ki bize final modeli ver kardeş, bağımsız değişkeni, bağımlı değişkeni ver
#bir parametre seç ve buna göre öğrenme eğrilerini ver istiyoruz
#bu bana numerik çıktılar vericek ben de görselleştiricem
#hangi parametre max depth
#hangi aralıkta gir
#hangi skoru görmek istersin
#kaç katlı cross validate atalım girdik

train_score, test_score = validation_curve(cart_final, X, y,
                                           param_name="max_depth",
                                           param_range=range(1, 11),
                                           scoring="roc_auc",
                                           cv=10)
#şimdi çıktı geldi de tamam nedir bu?
#şimdi bize çıktıdan arraylar içerisinde bazı sayılar geldi ne bunlar
#bu arraylar 9'uyla train 1'iyle testin cv=10'da sonuçları
#bunları nasıl kullanıcaz bu arrayların ortalamasını alarak
#model karmaşıklığına ne dedik train ve test hataları görselleştirilir
#veee ayrım noktası üzerinden karar vermeye çalışırız
mean_train_score = np.mean(train_score, axis=1)
mean_test_score = np.mean(test_score, axis=1)

#bu da bize train test görselini verecek fonksiyon aşaıda

plt.plot(range(1, 11), mean_train_score,
         label="Training Score", color='b')

plt.plot(range(1, 11), mean_test_score,
         label="Validation Score", color='g')

plt.title("Validation Curve for CART")
plt.xlabel("Number of max_depth")
plt.ylabel("AUC")
plt.tight_layout()
plt.legend(loc='best')
plt.show()
#çıktı görselinden anlıyoruz ki max derinlik 2 olduğunda başarımız artmaya devam etmiş
#3 olduğunda da artmış ama 4'te train test'in başarısı hala artmaya devam ediyor
#1'e kadar çıkmış skor ama test skoru düşmüş orada
#max derinliği biz zaten seçtik 5 (emin değilim) ama grafikte 3 gibi çıkıyor
#olay ne burada; biz model kurarken çok değişkenli olarak değerlendirip seçtik
#max derinliği tek başına optimum değeri seçmiyoruz
#biz bu görselle bi çıkarım yapıyoruz bakıyoruz nasılmış doğru şeyler yapmış mıyız diye



#kıyamadığım serisinden bir fonksiyon 
#dinamik bir fonksiyonkee
def val_curve_params(model, X, y, param_name, param_range, scoring="roc_auc", cv=10):
    train_score, test_score = validation_curve(
        model, X=X, y=y, param_name=param_name, param_range=param_range, scoring=scoring, cv=cv)

    mean_train_score = np.mean(train_score, axis=1)
    mean_test_score = np.mean(test_score, axis=1)

    plt.plot(param_range, mean_train_score,
             label="Training Score", color='b')

    plt.plot(param_range, mean_test_score,
             label="Validation Score", color='g')

    plt.title(f"Validation Curve for {type(model).__name__}")
    plt.xlabel(f"Number of {param_name}")
    plt.ylabel(f"{scoring}")
    plt.tight_layout()
    plt.legend(loc='best')
    plt.show(block=True)


val_curve_params(cart_final, X, y, "max_depth", range(1, 11), scoring="f1")

cart_val_params = [["max_depth", range(1, 11)], ["min_samples_split", range(2, 20)]]

for i in range(len(cart_val_params)):
    val_curve_params(cart_model, X, y, cart_val_params[i][0], cart_val_params[i][1])


#BONUS BİLGİ
################################################
# 8. Visualizing the Decision Tree
################################################

# conda install graphviz 
# import graphviz
#BU YUKARIDAKILERI KUTUPHANE CALISMAZSA DIYE

def tree_graph(model, col_names, file_name):
    tree_str = export_graphviz(model, feature_names=col_names, filled=True, out_file=None)
    graph = pydotplus.graph_from_dot_data(tree_str)
    graph.write_png(file_name)
#fonksiyon yukarıda 

tree_graph(model=cart_final, col_names=X.columns, file_name="cart_final.png")
#yukarıda çalıştırdık
#çalışma dizinine git yoksa diskten yeniden yükle de çift tıkla ve aç
#grafik de bayağı büyük gelicek he

cart_final.get_params()


################################################
# 9. Extracting Decision Rules
################################################

tree_rules = export_text(cart_final, feature_names=list(X.columns))
print(tree_rules)
#bu yaptığımız karar kurallarını konsolda gözlemleyebileceğimiz bir tarzda bize sunmuş oldu
#dallanmalardan sonra tüm değişkenler tekrar göz önünde bulunduruluyor bu arada


################################################
# 10. Extracting Python Codes of Decision Rules
################################################
#burada bir karar ağacı yöntemini canlı sisteme entegre edeceğizz

# sklearn '0.23.1' versiyonu ile yapılabilir.
# pip install scikit-learn==0.23.1

print(skompile(cart_final.predict).to('python/code'))

print(skompile(cart_final.predict).to('sqlalchemy/sqlite'))

print(skompile(cart_final.predict).to('excel'))

#yukarıda native'de lokalde kullanmak için ihtiyacımız olan kodları çıkarttık
#veri tabanının içinde çalışmak her zaman daha iyi 
#canlı ortamda nasıl kullanacaz babuş
#sql'den çıkmadan işimizi hallediyoruzkee
################################################
# 11. Prediction using Python Codes
################################################

def predict_with_rules(x):
    return ((((((0 if x[6] <= 0.671999990940094 else 1 if x[6] <= 0.6864999830722809 else
        0) if x[0] <= 7.5 else 1) if x[5] <= 30.949999809265137 else ((1 if x[5
        ] <= 32.45000076293945 else 1 if x[3] <= 10.5 else 0) if x[2] <= 53.0 else
        ((0 if x[1] <= 111.5 else 0 if x[2] <= 72.0 else 1 if x[3] <= 31.0 else
        0) if x[2] <= 82.5 else 1) if x[4] <= 36.5 else 0) if x[6] <=
        0.5005000084638596 else (0 if x[1] <= 88.5 else (((0 if x[0] <= 1.0 else
        1) if x[1] <= 98.5 else 1) if x[6] <= 0.9269999861717224 else 0) if x[1
        ] <= 116.0 else 0 if x[4] <= 166.0 else 1) if x[2] <= 69.0 else ((0 if
        x[2] <= 79.0 else 0 if x[1] <= 104.5 else 1) if x[3] <= 5.5 else 0) if
        x[6] <= 1.098000019788742 else 1) if x[5] <= 45.39999961853027 else 0 if
        x[7] <= 22.5 else 1) if x[7] <= 28.5 else (1 if x[5] <=
        9.649999618530273 else 0) if x[5] <= 26.350000381469727 else (1 if x[1] <=
        28.5 else ((0 if x[0] <= 11.5 else 1 if x[5] <= 31.25 else 0) if x[1] <=
        94.5 else (1 if x[5] <= 36.19999885559082 else 0) if x[1] <= 97.5 else
        0) if x[6] <= 0.7960000038146973 else 0 if x[0] <= 3.0 else (1 if x[6] <=
        0.9614999890327454 else 0) if x[3] <= 20.0 else 1) if x[1] <= 99.5 else
        ((1 if x[5] <= 27.649999618530273 else 0 if x[0] <= 5.5 else (((1 if x[
        0] <= 7.0 else 0) if x[1] <= 103.5 else 0) if x[1] <= 118.5 else 1) if
        x[0] <= 9.0 else 0) if x[6] <= 0.19999999552965164 else ((0 if x[5] <=
        36.14999961853027 else 1) if x[1] <= 113.0 else 1) if x[0] <= 1.5 else
        (1 if x[6] <= 0.3620000034570694 else 1 if x[5] <= 30.050000190734863 else
        0) if x[2] <= 67.0 else (((0 if x[6] <= 0.2524999976158142 else 1) if x
        [1] <= 120.0 else 1 if x[6] <= 0.23899999260902405 else 1 if x[7] <=
        30.5 else 0) if x[2] <= 83.0 else 0) if x[5] <= 34.45000076293945 else
        1 if x[1] <= 101.0 else 0 if x[5] <= 43.10000038146973 else 1) if x[6] <=
        0.5609999895095825 else ((0 if x[7] <= 34.5 else 1 if x[5] <=
        33.14999961853027 else 0) if x[4] <= 120.5 else (1 if x[3] <= 47.5 else
        0) if x[4] <= 225.0 else 0) if x[0] <= 6.5 else 1) if x[1] <= 127.5 else
        (((((1 if x[1] <= 129.5 else ((1 if x[6] <= 0.5444999933242798 else 0) if
        x[2] <= 56.0 else 0) if x[2] <= 71.0 else 1) if x[2] <= 73.0 else 0) if
        x[5] <= 28.149999618530273 else (1 if x[1] <= 135.0 else 0) if x[3] <=
        21.0 else 1) if x[4] <= 132.5 else 0) if x[1] <= 145.5 else 0 if x[7] <=
        25.5 else ((0 if x[1] <= 151.0 else 1) if x[5] <= 27.09999942779541 else
        ((1 if x[0] <= 6.5 else 0) if x[6] <= 0.3974999934434891 else 0) if x[2
        ] <= 82.0 else 0) if x[7] <= 61.0 else 0) if x[5] <= 29.949999809265137
         else ((1 if x[2] <= 61.0 else (((((0 if x[6] <= 0.18299999833106995 else
        1) if x[0] <= 0.5 else 1 if x[5] <= 32.45000076293945 else 0) if x[2] <=
        73.0 else 0) if x[0] <= 4.5 else 1 if x[6] <= 0.6169999837875366 else 0
        ) if x[6] <= 1.1414999961853027 else 1) if x[5] <= 41.79999923706055 else
        1 if x[6] <= 0.37299999594688416 else 1 if x[1] <= 142.5 else 0) if x[7
        ] <= 30.5 else (((1 if x[6] <= 0.13649999350309372 else 0 if x[5] <=
        32.45000076293945 else 1 if x[5] <= 33.05000114440918 else (0 if x[6] <=
        0.25599999725818634 else (0 if x[1] <= 130.5 else 1) if x[0] <= 8.5 else
        0) if x[0] <= 13.5 else 1) if x[2] <= 92.0 else 1) if x[5] <=
        45.54999923706055 else 1) if x[6] <= 0.4294999986886978 else (1 if x[5] <=
        40.05000114440918 else 0 if x[5] <= 40.89999961853027 else 1) if x[4] <=
        333.5 else 1 if x[2] <= 64.0 else 0) if x[1] <= 157.5 else ((((1 if x[7
        ] <= 25.5 else 0 if x[4] <= 87.5 else 1 if x[5] <= 45.60000038146973 else
        0) if x[7] <= 37.5 else 1 if x[7] <= 56.5 else 0 if x[6] <=
        0.22100000083446503 else 1) if x[6] <= 0.28849999606609344 else 0) if x
        [6] <= 0.3004999905824661 else 1 if x[7] <= 44.0 else (0 if x[7] <=
        51.0 else 1 if x[6] <= 1.1565000414848328 else 0) if x[0] <= 6.5 else 1
        ) if x[4] <= 629.5 else 1 if x[6] <= 0.4124999940395355 else 0)

X.columns

x = [12, 13, 20, 23, 4, 55, 12, 7]

predict_with_rules(x)

x = [6, 148, 70, 35, 0, 30, 0.62, 50]

predict_with_rules(x)



################################################
# 12. Saving and Loading Model
################################################

joblib.dump(cart_final, "cart_final.pkl")

cart_model_from_disc = joblib.load("cart_final.pkl")

x = [12, 13, 20, 23, 4, 55, 12, 7]

cart_model_from_disc.predict(pd.DataFrame(x).T)

















