from flask import Blueprint
from flask_restful import Api, Resource, reqparse
import json
import datetime
import markdown
import os

api_pages = Blueprint("api_pages", __name__)
api = Api(api_pages)

"""
TODO stripout MOA api and rewrite to call hpc patch  / inventoy
left for now so I don't need to rediscover all the quirks and syntax needed
all over again
"""

def getData(sql):
    conn = dbGetConn()
    curr = conn.cursor()
    curr.execute(sql)
    data = curr.fetchall()
    jsonData = [dict(zip([key[0] for key in curr.description], row)) for row in data]
    curr.close()
    conn.close()
    return jsonData if jsonData else None


def dump_date(thing):
    if isinstance(thing, datetime.datetime):
        return thing.isoformat()
    return thing


@api_pages.route("/")
def api_home():
    """Present some documentation"""

    # Open the README file
    with open(os.path.join(api_pages.root_path) + "/README.md", "r") as markdown_file:

        # Read the content of the file
        content = markdown_file.read()

        # Convert to HTML
        md = markdown.markdown(content, extensions=["tables", "fenced_code", "toc"])
        return md


class Entity(Resource):
    def get(self, id=None):
        if id is not None:
            sql = f"select * from MOA_ENTITY where entity_id={id}"
        else:
            sql = "select * from MOA_ENTITY"
        data = getData(sql)
        # set default handler to dump_date if there is a date object
        data = json.dumps(data, default=dump_date)
        data = json.loads(data)
        return data, 201


class Triple(Resource):
    def get(self, tripleid=None, subjectid=None, predicateid=None, objectid=None):
        if tripleid is not None:
            sql = f"select * from MOA_TRIPLE where triple_id={tripleid}"
        elif subjectid is not None:
            sql = f"select * from MOA_TRIPLE where subject_id={subjectid}"
        elif predicateid is not None:
            sql = f"select * from MOA_TRIPLE where predicate_id={predicateid}"
        elif objectid is not None:
            sql = f"select * from MOA_TRIPLE where object_id={objectid}"
        else:
            sql = "select * from MOA_TRIPLE"
        data = getData(sql)
        return data, 201


class Evidence(Resource):
    def get(self, evidenceid=None, evidenceTripleid=None):
        if evidenceid is not None:
            sql = f"select * from MOA_EVIDENCE where evidence_id={evidenceid}"
        elif evidenceTripleid is not None:
            sql = f"select * from MOA_EVIDENCE where triple_id={evidenceTripleid}"
        else:
            sql = "select * from MOA_EVIDENCE"
        data = getData(sql)
        return data, 201


class Group(Resource):
    def get(self, groupid=None, entityid=None):
        if groupid is not None:
            sql = f"select * from MOA_GROUP where MOA_GROUP_ID={groupid}"
        elif entityid is not None:
            sql = f"select * from MOA_GROUP where ENTITY_ID={entityid}"
        else:
            sql = "select * from MOA_GROUP"
        data = getData(sql)
        return data, 201


class SpeciesProtein(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument("species", type=str, location="args")
        self.reqparse.add_argument("uniprot", type=str, location="args")
        super(SpeciesProtein, self).__init__()

    def get(self, sprotid=None, entityid=None):
        args = self.reqparse.parse_args()
        if sprotid is not None:
            sql = (
                f"select * from MOA_SPECIES_PROTEIN where SPECIES_PROTEIN_ID={sprotid}"
            )
        elif entityid is not None:
            sql = f"select * from MOA_SPECIES_PROTEIN where ENTITY_ID={entityid}"
        elif args["species"] is not None:
            speccode = args["species"]
            sql = f"select * from MOA_SPECIES_PROTEIN where SPECIES_CODE='{speccode}'"
        elif args["uniprot"] is not None:
            uniprot = args["uniprot"]
            sql = f"select * from MOA_SPECIES_PROTEIN where UNIPROT_CODE='{uniprot}'"
        else:
            sql = "select * from MOA_SPECIES_PROTEIN"
        data = getData(sql)
        return data, 201


class EntityLink(Resource):
    def get(self, elid=None, entityid=None):
        if elid is not None:
            sql = f"select * from MOA_ENTITY_LINK where ID={elid}"
        elif entityid is not None:
            sql = f"select * from MOA_ENTITY_LINK where ENTITY_ID={entityid}"
        else:
            sql = "select * from MOA_ENTITY_LINK"
        data = getData(sql)
        return data, 201


class MClass(Resource):
    def get(self, clid=None):
        if clid is not None:
            sql = f"select * from MOA_CLASS where CLASS_ID={clid}"
        else:
            sql = "select * from MOA_CLASS"
        data = getData(sql)
        return data, 201


class Indication(Resource):
    def get(self, indicid=None, entityid=None):
        if indicid is not None:
            sql = f"select * from MOA_INDICATION where INDICATION_ID={indicid}"
        elif entityid is not None:
            sql = f"select * from MOA_INDICATION where ENTITY_ID={entityid}"
        else:
            sql = "select * from MOA_INDICATION"
        data = getData(sql)
        return data, 201


class Match(Resource):
    def get(self, matchid=None, synonym1=None, synonym2=None):
        if matchid is not None:
            sql = f"select * from MOA_MATCH where MATCH_ID={matchid}"
        elif synonym1 is not None:
            sql = f"select * from MOA_MATCH where SYNONYM_1={synonym1}"
        elif synonym2 is not None:
            sql = f"select * from MOA_MATCH where SYNONYM_2={synonym2}"
        else:
            sql = "select * from MOA_MATCH"
        data = getData(sql)
        return data, 201


class Predicate(Resource):
    def get(self, predicate=None):
        if predicate is not None:
            sql = f"select * from MOA_PREDICATE where PREDICATE_ID={predicate}"
        else:
            sql = "select * from MOA_PREDICATE"
        data = getData(sql)
        return data, 201


class Synonym(Resource):
    def get(self, synonymid=None, entityid=None):
        if synonymid is not None:
            sql = f"select * from MOA_SYNONYM where SYNONYM_ID={synonymid}"
        elif entityid is not None:
            sql = f"select * from MOA_SYNONYM where ENTITY_ID={entityid}"
        else:
            sql = "select * from MOA_SYNONYM"
        data = getData(sql)
        return data, 201


# Resources
# Entity
api.add_resource(Entity, "/entity", endpoint="entitys")
api.add_resource(Entity, "/entity/<int:id>", endpoint="entity")

# Triple
api.add_resource(Triple, "/triple", endpoint="triples")
api.add_resource(Triple, "/triple/<int:tripleid>", endpoint="triple")
api.add_resource(Triple, "/triple/triple/<int:tripleid>", endpoint="tripleid")
api.add_resource(Triple, "/triple/subject/<int:subjectid>", endpoint="subjectid")
api.add_resource(Triple, "/triple/predicate/<int:predicateid>", endpoint="predicateid")
api.add_resource(Triple, "/triple/object/<int:objectid>", endpoint="objectid")

# Evidence
api.add_resource(Evidence, "/evidence", endpoint="evidences")
api.add_resource(Evidence, "/evidence/<int:evidenceid>", endpoint="evidence")
api.add_resource(Evidence, "/evidence/evidence/<int:evidenceid>", endpoint="evidenceid")
api.add_resource(
    Evidence, "/evidence/triple/<int:evidenceTripleid>", endpoint="evidenceTripleid"
)
# Group
api.add_resource(Group, "/group", endpoint="groups")
api.add_resource(Group, "/group/<int:groupid>", endpoint="group")
api.add_resource(Group, "/group/group/<int:groupid>", endpoint="groupid")
api.add_resource(Group, "/group/entity/<int:entityid>", endpoint="entityid")

# SpeciesProtein
api.add_resource(SpeciesProtein, "/species-protein", endpoint="species-proteins")
api.add_resource(
    SpeciesProtein, "/species-protein/<int:sprotid>", endpoint="species-protein"
)
api.add_resource(
    SpeciesProtein,
    "/species-protein/species-protein/<int:sprotid>",
    endpoint="species-proteinid",
)
api.add_resource(
    SpeciesProtein, "/species-protein/entity/<int:entityid>", endpoint="sprentityid"
)
api.add_resource(SpeciesProtein, "/species-protein/species-code", endpoint="speccode")
api.add_resource(
    SpeciesProtein, "/species-protein/uniprot-code", endpoint="uniprotcode"
)
# EntityLink
api.add_resource(EntityLink, "/entity-link", endpoint="entitylinks")
api.add_resource(EntityLink, "/entity-link/<int:elid>", endpoint="entitylink")
api.add_resource(EntityLink, "/entity-link/entity-link/<int:elid>", endpoint="elid")
api.add_resource(
    EntityLink, "/entity-link/entity/<int:entityid>", endpoint="elentityid"
)

# Class
api.add_resource(MClass, "/class", endpoint="clids")
api.add_resource(MClass, "/class/<int:clid>", endpoint="clid")

# Indication
api.add_resource(Indication, "/indication", endpoint="indications")
api.add_resource(Indication, "/indication/<int:indicid>", endpoint="indication")
api.add_resource(
    Indication, "/indication/indication/<int:indicid>", endpoint="indicationid"
)
api.add_resource(
    Indication, "/indication/entity/<int:entityid>", endpoint="indicentityid"
)

# Match
api.add_resource(Match, "/match", endpoint="matches")
api.add_resource(Match, "/match/<int:matchid>", endpoint="match")
api.add_resource(Match, "/match/match/<int:matchid>", endpoint="matchid")
api.add_resource(Match, "/match/synonym-1/<int:synonym1>", endpoint="synonym1")
api.add_resource(Match, "/match/synonym-2/<int:synonym2>", endpoint="synonym2")

# Predicate
api.add_resource(Predicate, "/predicate", endpoint="predicates")
api.add_resource(Predicate, "/predicate/<int:predicate>", endpoint="predicate")

# Synonym
api.add_resource(Synonym, "/synonym", endpoint="synonyms")
api.add_resource(Synonym, "/synonym/<int:synonymid>", endpoint="synonym")
api.add_resource(Synonym, "/synonym/entity/<int:entityid>", endpoint="synonymentityid")
