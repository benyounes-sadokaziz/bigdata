# Presentation Outline - Big Data Project
## Kafka, Sqoop & Flume Integration

---

## Slide 1: Title Slide
- **Title**: Big Data Architecture with Kafka, Sqoop & Flume
- **Subtitle**: Real-time Streaming, ETL, and Log Processing
- **Your Name & Date**

---

## Slide 2: Table of Contents
1. Pourquoi le recours au Big Data?
2. À quel niveau le Big Data est utilisé?
3. Comment le Big Data a été utilisé?
4. Les outils: Kafka, Sqoop, Flume
5. Use Case et Démonstration
6. Architecture de la solution
7. Résultats et conclusions

---

## Slide 3-4: Pourquoi le recours au Big Data?

### Points à couvrir:
- **Volume**: Gestion de grandes quantités de données (TB/PB)
- **Vélocité**: Traitement en temps réel de flux de données
- **Variété**: Données structurées (SGBD), semi-structurées (logs), streaming
- **Limitations des solutions traditionnelles**:
  - SGBD relationnels limités en scalabilité
  - Traitement batch insuffisant pour temps réel
  - Coûts élevés de stockage traditionnel

### Votre use case:
- Besoin de synchroniser données transactionnelles (MySQL)
- Analyser logs d'applications en temps réel
- Intégrer flux de données streaming pour dashboards

---

## Slide 5-6: À quel niveau le Big Data est utilisé?

### Niveaux d'utilisation:
1. **Niveau Ingestion (Collecte)**:
   - Kafka: Collecte de flux temps réel
   - Flume: Agrégation de logs
   - Sqoop: Import/Export SGBD

2. **Niveau Stockage**:
   - HDFS: Data Lake centralisé
   - Distribution sur cluster

3. **Niveau Traitement**:
   - MapReduce/Spark (non implémenté mais mentionner)
   - Traitement batch et streaming

4. **Niveau Analyse et Visualisation**:
   - Possibilité d'intégrer Hive, Impala
   - Dashboards (Power BI, Grafana)

---

## Slide 7: Comment le Big Data a été utilisé?

### Architecture mise en place:
```
Sources de Données
    ├── MySQL (Données transactionnelles) ──Sqoop──▶ HDFS
    ├── Applications (Logs) ──Flume──▶ HDFS
    └── Flux temps réel ──Kafka──▶ Flume ──▶ HDFS
                            ▼
                    Analyse & Reporting
```

### Workflow:
1. **Batch Processing**: Sqoop import quotidien des tables MySQL
2. **Log Processing**: Flume collecte et agrège les logs d'applications
3. **Real-time Streaming**: Kafka capture événements temps réel
4. **Storage**: Tout converge vers HDFS pour analyse

---

## Slide 8-9: Apache Kafka - Streaming Platform

### Qu'est-ce que Kafka?
- Plateforme de streaming distribuée
- Publication/Souscription de messages
- Haute disponibilité et scalabilité

### Composants:
- **Producer**: Publie messages vers topics
- **Consumer**: Souscrit et consomme messages
- **Broker**: Serveur Kafka stockant messages
- **Topic**: Canal logique de messages
- **Partition**: Subdivision d'un topic pour parallélisme

### Utilisation dans notre projet:
- Flux de données temps réel (IoT, événements web)
- Intégration avec Flume pour persistance HDFS
- Buffer pour traitement asynchrone

### Installation (Docker):
```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    ports: ["2181:2181"]
  
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    ports: ["9092:9092"]
    depends_on: [zookeeper]
```

### Commandes essentielles:
```bash
# Créer un topic
kafka-topics --create --topic test-topic

# Producer
kafka-console-producer --topic test-topic

# Consumer
kafka-console-consumer --topic test-topic --from-beginning
```

---

## Slide 10-11: Apache Sqoop - ETL Tool

### Qu'est-ce que Sqoop?
- SQL to Hadoop
- Transfert bulk entre SGBD et HDFS
- Import et Export bidirectionnel

### Fonctionnalités:
- Import de tables complètes
- Import incrémental (append/lastmodified)
- Export vers SGBD
- Requêtes SQL personnalisées
- Support multi-SGBD (MySQL, PostgreSQL, Oracle)

### Utilisation dans notre projet:
- Import daily des données transactionnelles
- Synchronisation MySQL → HDFS
- Backup et archivage

### Installation (Docker):
```dockerfile
FROM bde2020/hadoop-base:2.0.0-hadoop3.2.1-java8
ENV SQOOP_VERSION=1.4.7
RUN wget sqoop-${SQOOP_VERSION}.tar.gz && \
    tar -xzf && mv to /opt/sqoop
```

### Commandes essentielles:
```bash
# Import table
sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --table employees \
  --target-dir /user/sqoop/employees

# Import avec WHERE
sqoop import \
  --table employees \
  --where "department='IT'"

# Import all tables
sqoop import-all-tables \
  --warehouse-dir /user/sqoop/warehouse
```

---

## Slide 12-13: Apache Flume - Log Aggregation

### Qu'est-ce que Flume?
- Système de collecte et agrégation de logs
- Architecture basée sur flux
- Fiabilité et scalabilité

### Composants:
- **Source**: Point d'entrée (spooldir, kafka, exec)
- **Channel**: Buffer (memory, file)
- **Sink**: Destination (HDFS, Kafka, HBase)

### Utilisation dans notre projet:
- Collecte de logs d'applications
- Agrégation multi-sources
- Persistance dans HDFS avec partitionnement temporel
- Intégration Kafka → HDFS

### Installation (Docker):
```dockerfile
FROM openjdk:8-jdk
ENV FLUME_VERSION=1.11.0
RUN wget apache-flume-${FLUME_VERSION}-bin.tar.gz && \
    tar -xzf && mv to /opt/flume
```

### Configuration exemple (flume-hdfs.conf):
```properties
agent1.sources = logSource
agent1.sinks = hdfsSink
agent1.channels = memoryChannel

agent1.sources.logSource.type = spooldir
agent1.sources.logSource.spoolDir = /logs/incoming

agent1.sinks.hdfsSink.type = hdfs
agent1.sinks.hdfsSink.hdfs.path = hdfs://namenode:9000/user/flume/logs/%Y/%m/%d
agent1.sinks.hdfsSink.hdfs.filePrefix = logs-
agent1.sinks.hdfsSink.hdfs.rollInterval = 60
```

### Commandes essentielles:
```bash
# Démarrer agent
flume-ng agent \
  --conf-file /opt/flume/conf/flume-hdfs.conf \
  --name agent1
```

---

## Slide 14: Use Case - [Votre Cas Spécifique]

### Contexte:
- **Entreprise**: [Exemple: E-commerce platform]
- **Problématique**: 
  - Analyser comportement utilisateurs en temps réel
  - Synchroniser données transactionnelles pour BI
  - Centraliser logs de microservices

### Données utilisées:
- **MySQL**: Tables employees, sales (données transactionnelles)
- **Logs**: Fichiers logs d'applications (access logs, error logs)
- **Streaming**: Événements utilisateurs (clicks, achats)

### Objectifs:
1. Créer un Data Lake unifié (HDFS)
2. Pipeline ETL automatisé (Sqoop)
3. Monitoring temps réel (Kafka + Flume)
4. Historisation des logs (Flume → HDFS)

---

## Slide 15: Architecture Détaillée

[Diagramme montrant:]

```
┌─────────────────────────────────────────────────────┐
│                   Data Sources                       │
├─────────────────────────────────────────────────────┤
│  MySQL DB  │  Log Files  │  Real-time Events        │
└──────┬──────────┬─────────────────┬─────────────────┘
       │          │                 │
       │ Sqoop    │ Flume           │ Kafka
       │          │                 │
       ▼          ▼                 ▼
┌─────────────────────────────────────────────────────┐
│              HDFS Data Lake                          │
│  /user/sqoop/employees/                             │
│  /user/sqoop/sales/                                 │
│  /user/flume/logs/2024/11/10/                       │
│  /user/flume/kafka-data/                            │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│         Processing & Analytics Layer                 │
│  (Hive, Spark, MapReduce - future work)            │
└─────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│            Visualization Layer                       │
│  (Power BI, Tableau, Dashboards)                    │
└─────────────────────────────────────────────────────┘
```

### Technologies utilisées:
- **Orchestration**: Docker Compose
- **Storage**: Hadoop HDFS 3.2.1
- **Coordination**: Zookeeper
- **Streaming**: Kafka 7.5.0
- **ETL**: Sqoop 1.4.7
- **Log Processing**: Flume 1.11.0
- **Database**: MySQL 8.0

---

## Slide 16: Étapes d'Installation

### Prérequis:
- Windows 10/11 avec WSL2
- Docker Desktop (8GB RAM minimum)
- 20GB espace disque

### Installation:
1. **Setup Docker Compose**:
   ```bash
   docker-compose up -d
   ```

2. **Vérification**:
   ```bash
   docker-compose ps
   ```

3. **Services exposés**:
   - Kafka UI: http://localhost:8080
   - HDFS NameNode: http://localhost:9870
   - MySQL: localhost:3306

### Temps d'installation: ~5 minutes
### Temps de démarrage: ~60 secondes

---

## Slide 17-18: Démonstration - Kafka

### Test 1: Message Streaming

**Étape 1 - Créer un topic**:
```bash
docker exec kafka kafka-topics --create \
  --topic sales-events \
  --partitions 3
```

**Étape 2 - Produire des messages**:
```bash
docker exec kafka kafka-console-producer \
  --topic sales-events
> {"product":"Laptop","price":1200,"quantity":1}
> {"product":"Mouse","price":25,"quantity":5}
```

**Étape 3 - Consommer des messages**:
```bash
docker exec kafka kafka-console-consumer \
  --topic sales-events \
  --from-beginning
```

**Résultat attendu**: Messages affichés en temps réel

[Screenshot de la Kafka UI montrant le topic et les messages]

---

## Slide 19-20: Démonstration - Sqoop

### Test 2: MySQL to HDFS Import

**Étape 1 - Voir données source (MySQL)**:
```bash
docker exec mysql mysql -usqoop -psqoop123 testdb \
  -e "SELECT * FROM employees;"
```

**Étape 2 - Import vers HDFS**:
```bash
docker exec sqoop sqoop import \
  --connect jdbc:mysql://mysql:3306/testdb \
  --table employees \
  --target-dir /user/sqoop/employees \
  --m 1
```

**Étape 3 - Vérifier dans HDFS**:
```bash
docker exec namenode hdfs dfs -ls /user/sqoop/
docker exec namenode hdfs dfs -cat /user/sqoop/employees/part-m-00000
```

**Résultat attendu**: 
- 8 employés importés
- Fichiers part-m-* dans HDFS

[Screenshot HDFS Web UI montrant les fichiers importés]

---

## Slide 21-22: Démonstration - Flume

### Test 3: Log Processing to HDFS

**Étape 1 - Générer des logs**:
```bash
docker exec flume bash /tmp/generate-logs.sh
```

**Étape 2 - Démarrer agent Flume**:
```bash
docker exec flume flume-ng agent \
  --conf-file /opt/flume/conf/flume-hdfs.conf \
  --name agent1
```

**Étape 3 - Vérifier dans HDFS**:
```bash
docker exec namenode hdfs dfs -ls -R /user/flume/logs/
docker exec namenode hdfs dfs -cat \
  /user/flume/logs/2024/11/10/logs-*.log
```

**Résultat attendu**: 
- Logs organisés par date (partitionnement temporel)
- Fichiers .log dans HDFS

[Screenshot HDFS montrant la structure /user/flume/logs/YYYY/MM/DD/]

---

## Slide 23: Test d'Intégration Complète

### Pipeline End-to-End:

1. **Données transactionnelles** (MySQL) → Sqoop → HDFS
2. **Logs d'applications** → Flume → HDFS  
3. **Événements temps réel** → Kafka → Flume → HDFS

### Commandes:
```bash
# 1. Import MySQL
docker exec sqoop sqoop import --table sales ...

# 2. Stream to Kafka
echo "New sale event" | kafka-console-producer --topic sales-stream

# 3. Generate logs
docker exec flume bash /tmp/generate-logs.sh

# 4. Verify in HDFS
docker exec namenode hdfs dfs -ls -R /user/
```

**Résultat**: Data Lake unifié avec données de 3 sources différentes

---

## Slide 24: Avantages de la Solution

### Avantages techniques:
- ✓ **Scalabilité**: Architecture distribuée
- ✓ **Fiabilité**: Réplication et fault-tolerance
- ✓ **Performance**: Traitement parallèle
- ✓ **Flexibilité**: Support multi-sources

### Avantages métier:
- ✓ **Centralisation**: Un seul Data Lake
- ✓ **Temps réel**: Réactivité business
- ✓ **Historisation**: Analyse temporelle
- ✓ **Coûts**: Storage distribué moins cher

---

## Slide 25: Défis Rencontrés

### Défis techniques:
- Configuration réseau Docker (Kafka advertised listeners)
- Compatibilité versions Hadoop/Sqoop
- Gestion mémoire containers

### Solutions:
- Utilisation Docker Compose avec networks
- Images officielles testées
- Allocation ressources optimisée

---

## Slide 26: Améliorations Futures

### Court terme:
- Ajouter Hive pour requêtes SQL sur HDFS
- Implémenter Spark pour traitement
- Dashboard Power BI

### Long terme:
- Cluster Hadoop multi-nœuds
- Machine Learning pipeline
- Real-time analytics avec Spark Streaming
- Data governance (Atlas, Ranger)

---

## Slide 27: Monitoring & Observabilité

### Outils actuels:
- Kafka UI (http://localhost:8080)
- HDFS Web UI (http://localhost:9870)
- Docker logs

### Métriques importantes:
- Kafka: Throughput, lag, partitions
- HDFS: Storage utilization, block health
- Flume: Events processed, channel capacity

---

## Slide 28: Conclusion

### Objectifs atteints:
- ✓ Architecture Big Data fonctionnelle
- ✓ 3 outils intégrés (Kafka, Sqoop, Flume)
- ✓ Pipeline data complet
- ✓ Démonstration pratique

### Apprentissages:
- Mise en place infrastructure Big Data
- Intégration d'outils distribués
- Containerisation avec Docker
- Best practices Big Data

### Impact:
- Data Lake centralisé et évolutif
- Fondation pour analytics avancés
- Réduction time-to-insight

---

## Slide 29: Questions & Réponses

**Questions fréquentes**:

Q: Pourquoi Docker plutôt qu'installation native?
A: Portabilité, isolation, facilité deployment

Q: Peut-on ajouter d'autres sources de données?
A: Oui, Kafka connectors, Flume sources multiples

Q: Performance sur un seul nœud?
A: Suffisant pour dev/test, production nécessite cluster

---

## Slide 30: Références

### Documentation:
- Apache Kafka: https://kafka.apache.org/documentation/
- Apache Sqoop: https://sqoop.apache.org/docs/1.4.7/
- Apache Flume: https://flume.apache.org/documentation.html
- Hadoop: https://hadoop.apache.org/docs/current/

### Code source:
- GitHub repository: [Votre lien]
- Docker Hub images utilisées

### Contact:
- [Votre email]
- [Votre LinkedIn]

---

## Annexes - Pour votre document

### A. Fichiers de configuration complets
- docker-compose.yml
- hadoop.env
- flume-hdfs.conf
- flume-kafka-hdfs.conf

### B. Scripts d'installation
- verify-setup.sh
- generate-logs.sh
- sqoop examples

### C. Screenshots
- Kafka UI
- HDFS Web UI
- Terminal commands output

### D. Logs d'exécution
- Kafka topic creation
- Sqoop import logs
- Flume agent logs

### E. Résultats HDFS
- Directory structure
- Sample data files
- File metadata
