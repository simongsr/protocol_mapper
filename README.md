# ProtocolMapper

## What is ProtocolMapper?
---

Good question... I don't know the answer!
This paragraph was written just because anyone expects it; next I will expose
you the problem that brought me to write ProtocolMapper and after that what it
does to solve it.


## The problem
---

Sono un programmatore backend da molto tempo ormai, la difficoltà principale
che incontro è quella di dover mappare delle informazioni tra due differenti
archivi, per quanto mi sia sforzato non sono riuscito a trovare alcuno
strumento in grado di automatizzare questo compito.

Ti faccio un esempio, ho un archivio sul cloud nel quale conservo la rubrica di
tutti i miei utenti, i quali accedono alle informazioni cui hanno diritto
mediante un'app sullo smartphone; l'app conserva la lista dei contatti in un DB
locale di modo che sia accessibile anche in assenza di connessione ad Internet.

Attualmente per risolvere questo problema devo mappare le entità sul cloud e
quelle sul dispositivo su un opportuno DTO, il quale verrà poi serializzato e
deserializzato. Non è detto che il backend sul cloud e quello sul dispositivo
siano stati scritti usando la stessa tecnologia, pertanto, in generale, dovrò
scrivere gli stessi DTO in due modi differenti. Ma non finisce qui, le azioni
che andranno implementate per mappare i DTO sulle entità sono di poco diverse,
ma andranno codificate tutte a mano.


## The solution
---

ProtocolMapper (chiaramente ispirato da ProtocolMapper di Google) si propone di
descrivere un'interfaccia indipendente dal linguaggio di programmazione e dai
framework usati dell'applicazione che stai sviluppando.

Non sai dove il tuo lavoro di porterà, i requisiti evolvono più velocemente
dello sviluppo! ;)

L'implementazione di una specifica istanza di un'interfaccia viene generata da
un builder usando dei templates, tutto 100% open source!


## A brief introduction to ProtocolMapper Interface Definition (PMID)
---


### Enum

Un enumeratore è un oggetto che specifica un insieme finito di informazioni, 
le quali possono essere assegnate ad un campo in maniera esclusiva (solo una 
alla volta per la stessa istanza del campo).

```
enum Pet {
    dog,               # = 0
    cat,               # = 1
    rabbit = 'Rabbit'  # = 'Rabbit'
}
```

Ad ogni elemento dell'enumeratore è possibile assegnare un valore mediante 
l'operatore di assegnamento; se un valore non viene specificato viene assegnato 
l'indice a base zero dell'elemento nell'enumeratore.

---


### Model


Definendo un oggetto di tipo __Model__ si sta di fatto dichiarando la struttura 
di una entità; vediamo un esempio:

```
# this is a comment

model Contact {
    required string name           = 1;
    required string phone_number   = 2 [regex = "^\+?\d{10}$"];
    optional string pet_name       = 3;
    repeated string common_friends = 4;
}
```

Lo snippet sopra dichiara l'entità `Contact`, la quale contiene quattro campi 
espliciti: `name`, `phone_number`, `pet_name`, `common_friends`.

La dichiarazione di un campo comporta la specifica della sua molteplicità, che 
può essere:
-  `required` - deve contenere uno ed un solo valore, nel caso non venga 
specificato viene sollevata un'eccezione in fase di persistenza;
- `optional` - può contenere un solo valore, nel caso non venga specificato 
viene utilizzato quello di default;
- `repeated` - può contenere una collezione di valori, di default è un insieme 
vuoto.

Il tipo di dato può essere un tipo primitivo:
- double
- float
- int32
- int64
- uint32
- uint64
- sint32
- sint64
- fixed32
- fixed64
- sfixed32
- sfixed64
- int
- long
- date
- timestamp
- time
- bool
- string
- bytes

oppure un riferimento ad un altro modello, in questo caso il nome del modello 
deve essere un nome completamente qualificato (composto dall'intero path), es.:

```
model Child {
    ...
}

model Parent {

    model Child {
        ...
    }

    required Child        child1 = 1;  # si riferisce al modello Child esterno
    required Parent.Child child2 = 2;  # si riferisce al modello Child annidato
}
```

Ricapitolando, la dichiarazione di un campo ha la struttura 
"`<multiplicity> <data_type> <field_name> = <field_id>;`".

---


#### Modificatori

Nel primo snippet si può vedere che il campo `phone_number` possiede 
un'informazione in più rispetto agli altri (`[regex = "^\+?\d{10}$"]`), 
la struttura riportata dentro le parentesi quadre indentifica un _modificatore_.

I modificatori possono essere applicati ai campi, ai modelli ed ai messaggi; 
per quanto riguarda modelli e messaggi i modificatori devono essere 
dichiarati tra il nome dell'oggetto e la parentesi graffa di apertura, es.:

```
model Contact [cacheable] [name = "cloud_contact"] {
    ...
}
```

Se il modicatore contiene solo il nome, il valore assegnatogli sarà di default 
`true`; è possibile assegnargli un valore mediante l'operatore di assegnamento 
(`=`).

#### Il modificatore `builtin`

Il modificatore `builtin` serve per comunicare al builder che il modello 
non deve essere generato.

Si immagini il caso in cui si intenda generare l'interfaccia per 
un'applicazione che fa uso di un framework, ad esempio __Django__ per 
__Python__; questo framework possiede già un modello per la rappresentazione di 
un utente (`django.contrib.auth.models.User`). Volendo integrare lo _schema_ 
con questo modello è necessario provvederne una rappresentazione in cui i campi 
vengono mappati su degli ID, il modello non deve però essere generato 
altrimenti si introdurrebbe un mismatch nella struttura del DB; questo è il 
caso in cui usare il modificatore `builtin`.


### Message

Un messaggio è un DTO.

```
message Phone_Book_Entry {
    required string name      = 1;  # mapped on Contact.name field
    required string phone_num = 2;  # mapped on Contact.phone_number field
    optional int    call_num;       # no mapping
}
```

La dichiarazione di un _messaggio_ è sostanzialmente analoga a quella di un 
_modello_, lo stesso vale per i campi; la differenza principale sta nel fatto 
che il _messaggio_ non viene persistito, il suo scopo è quello di trasferire 
informazioni. Altra differenza importante è quella che i campi di un messaggio 
non necessitano di un ID; se un campo ne possiede uno viene mappato sul 
corrispettivo del modello (se ne esiste uno, altrimenti viene trattato come 
non mappato).

Il tipo di dato di un campo di un messaggio può essere un tipo primitivo oppure 
un riferimento ad un altro messaggio.

---


### Reserved

La direttiva `reserved` serve ad impedire che un insieme di ID venga usato in 
una procedura di build.

```
reserved 1001;            # reserves just one ID
reserved 1003, 1005, 73;  # reserves three IDs (unordered)
reserved [1010, 1019];    # reserves ten IDS (including boudaries; ordered)
```

I motivi sono sostanzialmente due, si vogliono riservare degli ID per uso 
futuro, oppure si vuole impedire l'uso di campi deprecati per mantenere la 
retrocompatibilità con vecchie versioni del software.

---


### Variable declaration

Si possono dichiarare delle variabili con visibilità di modulo, ossia, che 
hanno validità all'interno del file nel quale sono state definite; si dichiara 
un nome e vi si assegna un valore mediante l'operatore di assegnamento.

```
VARIABLE_1 = 89
VARIABLE_2 = 'Hello, world!'
```

La dichiarazione di una variabile non necessita del punto e virgola finale.

---


### Alias

L'alias è un ulterire costrutto finalizzato al disaccoppiamento ed alla 
riusabilità dei moduli.

```
alias USER User  # alias declaration

model User_Profile {
    required USER user = 1;
    optional int  age  = 2;
}
```

Si supponga di dover generare un'interfaccia ed un wrapper per due framework 
che possiedono già due differenti implementazioni di un oggetto __user__; 
riferendosi all'alias, durante le dichiarazioni, si rende possibile la 
descrizione di uno schema indipendente dall'implementazione. In fase di 
generazione si possono inserire due differenti moduli che dichiarino due 
differenti modelli _builtin_.

---


### Config

Un file __config__ serve per dichiarare le build ed i profili.

---


## Further improvements

Further improvements
