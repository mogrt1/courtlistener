from collections import OrderedDict

from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from cl.api.utils import HyperlinkedModelSerializerWithId
from cl.audio.models import Audio
from cl.custom_filters.templatetags.extras import get_highlight
from cl.lib.document_serializer import (
    DocumentSerializer,
    NullableListField,
    TimeStampField,
)
from cl.people_db.models import PartyType, Person
from cl.recap.api_serializers import FjcIntegratedDatabaseSerializer
from cl.search.constants import o_type_index_map
from cl.search.documents import AudioDocument, OpinionDocument, PersonDocument
from cl.search.models import (
    PRECEDENTIAL_STATUS,
    Citation,
    Court,
    Docket,
    DocketEntry,
    Opinion,
    OpinionCluster,
    OpinionsCited,
    OriginatingCourtInformation,
    RECAPDocument,
    Tag,
)

inverted_o_type_index_map = {
    value: key for key, value in o_type_index_map.items()
}


class PartyTypeSerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    party_type = serializers.CharField(source="name")

    class Meta:
        model = PartyType
        fields = (
            "party",
            "party_type",
        )


class OriginalCourtInformationSerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    class Meta:
        model = OriginatingCourtInformation
        fields = "__all__"


class DocketSerializer(DynamicFieldsMixin, HyperlinkedModelSerializerWithId):
    court = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="court-detail",
        queryset=Court.objects.exclude(jurisdiction=Court.TESTING_COURT),
    )
    court_id = serializers.ReadOnlyField()
    original_court_info = OriginalCourtInformationSerializer(
        source="originating_court_information",
    )
    idb_data = FjcIntegratedDatabaseSerializer()
    clusters = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="opinioncluster-detail",
        queryset=OpinionCluster.objects.all(),
        style={"base_template": "input.html"},
    )
    audio_files = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="audio-detail",
        queryset=Audio.objects.all(),
        style={"base_template": "input.html"},
    )
    assigned_to = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )
    referred_to = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )
    absolute_url = serializers.CharField(
        source="get_absolute_url", read_only=True
    )

    class Meta:
        model = Docket
        exclude = (
            "view_count",
            "parties",
            "originating_court_information",
            "filepath_local",
        )


class RECAPDocumentSerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    tags = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="tag-detail",
        queryset=Tag.objects.all(),
        style={"base_template": "input.html"},
    )
    absolute_url = serializers.CharField(
        source="get_absolute_url", read_only=True
    )

    class Meta:
        model = RECAPDocument
        exclude = ("docket_entry",)


class DocketEntrySerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    docket = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="docket-detail",
        queryset=Docket.objects.all(),
        style={"base_template": "input.html"},
    )
    recap_documents = RECAPDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = DocketEntry
        fields = "__all__"


class FullDocketSerializer(DocketSerializer):
    docket_entries = DocketEntrySerializer(many=True, read_only=True)


class CourtSerializer(DynamicFieldsMixin, HyperlinkedModelSerializerWithId):
    class Meta:
        model = Court
        exclude = ("notes",)


class OpinionSerializer(DynamicFieldsMixin, HyperlinkedModelSerializerWithId):
    absolute_url = serializers.CharField(
        source="get_absolute_url", read_only=True
    )
    cluster_id = serializers.ReadOnlyField()
    cluster = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="opinioncluster-detail",
        queryset=OpinionCluster.objects.all(),
        style={"base_template": "input.html"},
    )
    author_id = serializers.ReadOnlyField()
    author = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )
    joined_by = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )

    class Meta:
        model = Opinion
        fields = "__all__"


class OpinionsCitedSerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    # These attributes seem unnecessary and this endpoint serializes the same
    # data without them, but when they're not here the API does a query that
    # pulls back ALL Opinions.
    citing_opinion = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="opinion-detail",
        queryset=Opinion.objects.all(),
        style={"base_template": "input.html"},
    )
    cited_opinion = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="opinion-detail",
        queryset=Opinion.objects.all(),
        style={"base_template": "input.html"},
    )

    class Meta:
        model = OpinionsCited
        fields = "__all__"


class CitationSerializer(ModelSerializer):
    class Meta:
        model = Citation
        exclude = (
            "id",
            "cluster",
        )


class OpinionClusterSerializer(
    DynamicFieldsMixin, HyperlinkedModelSerializerWithId
):
    absolute_url = serializers.CharField(
        source="get_absolute_url", read_only=True
    )
    panel = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )
    non_participating_judges = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="person-detail",
        queryset=Person.objects.all(),
        style={"base_template": "input.html"},
    )
    docket_id = serializers.ReadOnlyField()
    docket = serializers.HyperlinkedRelatedField(
        many=False,
        view_name="docket-detail",
        queryset=Docket.objects.all(),
        style={"base_template": "input.html"},
    )
    sub_opinions = serializers.HyperlinkedRelatedField(
        many=True,
        view_name="opinion-detail",
        queryset=Opinion.objects.all(),
        style={"base_template": "input.html"},
    )
    citations = CitationSerializer(many=True)

    class Meta:
        model = OpinionCluster
        fields = "__all__"


class TagSerializer(DynamicFieldsMixin, HyperlinkedModelSerializerWithId):
    class Meta:
        model = Tag
        fields = "__all__"


class SearchResultSerializer(serializers.Serializer):
    """The serializer for search results.

    Does not presently support the fields argument.
    """

    def update(self, instance, validated_data):
        raise NotImplementedError

    def create(self, validated_data):
        raise NotImplementedError

    solr_field_mappings = {
        "boolean": serializers.BooleanField,
        "string": serializers.CharField,
        "text_en_splitting_cl": serializers.CharField,
        "text_no_word_parts": serializers.CharField,
        "date": serializers.DateTimeField,
        # Numbers
        "int": serializers.IntegerField,
        "tint": serializers.IntegerField,
        "long": serializers.IntegerField,
        # schema.SolrFloatField: serializers.FloatField,
        # schema.SolrDoubleField: serializers.IntegerField,
        # Other
        "pagerank": serializers.CharField,
    }
    skipped_fields = ["_version_", "django_ct", "django_id", "text"]

    def get_fields(self):
        """Return a list of fields so that they don't have to be declared one
        by one and updated whenever there's a new field.
        """
        fields = {
            "snippet": serializers.CharField(read_only=True),
        }
        # Map each field in the Solr schema to a DRF field
        for field in self._context["schema"]["fields"]:
            if field.get("multiValued"):
                drf_field = serializers.ListField
            else:
                drf_field = self.solr_field_mappings[field["type"]]
            fields[field["name"]] = drf_field(read_only=True)

        for field in self.skipped_fields:
            if field in fields:
                fields.pop(field)
        fields = OrderedDict(sorted(fields.items()))  # Sort by key
        return fields


class OAESResultSerializer(DocumentSerializer):
    """The serializer for Oral argument results."""

    snippet = serializers.CharField(read_only=True)
    panel_ids = serializers.ListField(read_only=True)

    class Meta:
        document = AudioDocument
        exclude = (
            "text",
            "docket_slug",
            "percolator_query",
            "case_name_full",
            "dateArgued_text",
            "dateReargued_text",
            "dateReargumentDenied_text",
            "court_id_text",
        )


class PersonESResultSerializer(DocumentSerializer):
    """The serializer for Person results."""

    class Meta:
        document = PersonDocument
        exclude = ("text", "person_child")


class ExtendedPersonESSerializer(PersonESResultSerializer):
    """Extends the Person serializer with all the field we get from the db"""

    snippet = serializers.CharField(read_only=True)
    appointer = serializers.ListField(read_only=True)
    court = serializers.ListField(read_only=True)
    court_exact = serializers.ListField(read_only=True)
    position_type = serializers.ListField(read_only=True)
    supervisor = serializers.ListField(read_only=True)
    predecessor = serializers.ListField(read_only=True)
    date_nominated = serializers.ListField(read_only=True)
    date_elected = serializers.ListField(read_only=True)
    date_recess_appointment = serializers.ListField(read_only=True)
    date_referred_to_judicial_committee = serializers.ListField(read_only=True)
    date_judicial_committee_action = serializers.ListField(read_only=True)
    date_hearing = serializers.ListField(read_only=True)
    date_confirmation = serializers.ListField(read_only=True)
    date_start = serializers.ListField(read_only=True)
    date_granularity_start = serializers.ListField(read_only=True)
    date_retirement = serializers.ListField(read_only=True)
    date_termination = serializers.ListField(read_only=True)
    date_granularity_termination = serializers.ListField(read_only=True)
    judicial_committee_action = serializers.ListField(read_only=True)
    nomination_process = serializers.ListField(read_only=True)
    selection_method = serializers.ListField(read_only=True)
    selection_method_id = serializers.ListField(read_only=True)
    termination_reason = serializers.ListField(read_only=True)


class OpinionESResultSerializer(DocumentSerializer):
    """The serializer for Opinion results."""

    cluster_id = serializers.IntegerField(read_only=True)

    # Fields from the opinion child
    id = serializers.IntegerField(read_only=True)
    snippet = serializers.SerializerMethodField(read_only=True)
    author_id = serializers.IntegerField(read_only=True)
    type = serializers.SerializerMethodField(read_only=True)
    download_url = serializers.CharField(read_only=True)
    local_path = serializers.CharField(read_only=True)
    cites = NullableListField(read_only=True)
    joined_by_ids = NullableListField(read_only=True)
    panel_ids = NullableListField(read_only=True)
    sibling_ids = NullableListField(read_only=True)
    citation = NullableListField(read_only=True)
    per_curiam = serializers.BooleanField(read_only=True)
    court_exact = serializers.CharField(read_only=True, source="court_id")
    timestamp = TimeStampField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_type(self, obj):
        return inverted_o_type_index_map.get(obj.type)

    def get_status(self, obj):
        return PRECEDENTIAL_STATUS.get_status_value_reverse(obj.status)

    def get_snippet(self, obj):
        return get_highlight(obj, "text")

    class Meta:
        document = OpinionDocument
        exclude = (
            "text",
            "caseNameFull",
            "dateFiled_text",
            "dateArgued_text",
            "dateReargued_text",
            "type_text",
            "dateReargumentDenied_text",
            "posture",
            "syllabus",
            "procedural_history",
            "panel_names",
            "sha1",
        )
