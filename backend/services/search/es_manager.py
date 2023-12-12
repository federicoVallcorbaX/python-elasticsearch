from elasticsearch import Elasticsearch
from elasticsearch_dsl import (
    Completion,
    DenseVector,
    Document,
    Index,
    Keyword,
    MetaField,
    Short,
    Text,
    analyzer,
    token_filter,
)


ES_INDEX_NAME = "charla-python-v1.0"
ELASTICSEARCH_URL = "http://elasticsearch:9200"

ES_DENSE_VECTOR_M_VALUE = 16
ES_DENSE_VECTOE_EF_CONSTRUCTION_VALUE = 50


class ESManager:
    def __init__(self) -> None:
        self.index_name = ES_INDEX_NAME
        self.es_client = Elasticsearch(ELASTICSEARCH_URL)

    def _get_index_definition(self) -> Index:
        index = Index(self.index_name)
        index.settings(number_of_shards=1, number_of_replicas=0)
        return index

    def _get_default_analyzer(self) -> analyzer:
        english_stopwords = token_filter(
            "english_stopwords", "stop", stopwords="_english_"
        )
        english_stemmer = token_filter("english_stemmer", "stemmer", language="english")
        english_possessive_stemmer = token_filter(
            "english_possessive_stemmer", "stemmer", language="possessive_english"
        )
        default_analyzer = analyzer(
            "default_analyzer",
            tokenizer="whitespace",
            filter=[
                english_possessive_stemmer,
                "lowercase",
                english_stopwords,
                english_stemmer,
            ],
            char_filter=["html_strip"],
        )
        return default_analyzer

    def _get_trigram_analyzer(self) -> analyzer:
        shingle_filter = token_filter(
            "shingle_filter", "shingle", min_shingle_size=2, max_shingle_size=3
        )
        trigram_analyzer = analyzer(
            "custom", tokenizer="standard", filter=[shingle_filter]
        )
        return trigram_analyzer

    def get_document_definition(
        self,
        text_analyzer: type[analyzer] | None = None,
    ) -> Document:
        if not text_analyzer:
            text_analyzer = self._get_default_analyzer()
        trigram_analyzer = self._get_trigram_analyzer()

        class MovieDoc(Document):
            tmdbId = Keyword()
            item_id = Keyword()
            title = Text(
                analyzer=text_analyzer,
                fields={
                    # "completion": Completion(),
                    "trigram": Text(analyzer=trigram_analyzer),
                },
            )
            title_completion = Completion()
            year = Short()
            overview = Text(analyzer=text_analyzer)
            runtime = Short()
            genres = Keyword(multi=True)
            vote_average = Short()
            director = Keyword()
            protagonists = Keyword(multi=True)
            backdrop_path = Keyword()
            poster_path = Keyword()
            popularity = Short()

            openai_embedding = DenseVector(
                dims=1536,
                index=True,
                similarity="cosine",
                index_options={
                    "type": "hnsw",
                    "m": ES_DENSE_VECTOR_M_VALUE,
                    "ef_construction": ES_DENSE_VECTOE_EF_CONSTRUCTION_VALUE,
                },
            )
            sbert_symmetric_embedding = DenseVector(
                dims=768,
                index=True,
                similarity="cosine",
                index_options={
                    "type": "hnsw",
                    "m": ES_DENSE_VECTOR_M_VALUE,
                    "ef_construction": ES_DENSE_VECTOE_EF_CONSTRUCTION_VALUE,
                },
            )
            sbert_asymmetric_embedding = DenseVector(
                dims=768,
                index=True,
                similarity="dot_product",
                index_options={
                    "type": "hnsw",
                    "m": ES_DENSE_VECTOR_M_VALUE,
                    "ef_construction": ES_DENSE_VECTOE_EF_CONSTRUCTION_VALUE,
                },
            )

            class Meta:
                dynamic = MetaField("false")

        return MovieDoc

    def _create_index(self) -> Index:
        index = self._get_index_definition()
        document = self.get_document_definition()
        index.document(document)
        index.create(using=self.es_client)

    def create_index(self, drop_index_if_exists: bool = False) -> None:
        if self.es_client.indices.exists(index=self.index_name):
            if drop_index_if_exists:
                self.es_client.indices.delete(index=self.index_name)
            else:
                return
        self._create_index()

    def save_document(self, document_dict: dict) -> None:
        document = self.get_document_definition()()
        try:
            for key in document_dict:
                document[key] = document_dict[key]
            document.save(index=self.index_name, using=self.es_client)
        except:
            breakpoint()
