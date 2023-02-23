from django.db import models

# Create your models here.


class RootModel(models.Model):
    """
    Base Class for all other classes. Needs to be concrete class, not abstract, so that the id field that django auto-creates resides in this base model's db-table and is thusly inherited by all child models. 
    This makes the id-space across all models in the hierarchy distinct, i.e. two instances from two different child models can never have the same id. 

    :param models: _description_
    :type models: _type_
    """
    _child_model_lookup = {}

    def values(self):
        # just an example of a function to be inherited by all models, implements the functionality given in models.Model.objects.values()
        return {f.name: getattr(self, f.name) for f in self._meta.fields if not f.name.endswith("_ptr")}

    def values_list(self):
        # another example, implements the functionality given in models.Model.objects.values_list()
        return [getattr(self, f.name) for f in self._meta.fields if not f.name.endswith("_ptr")]

    @classmethod
    def get_fields(cls):
        # method only returns fields that a User should interact with
        return [f for f in cls._meta.fields if not f.name.endswith("_ptr")]

    @classmethod
    def get_submodels(cls):
        """
        _summary_ Recursive class-method that returns a list of all submodels (i.e. instances of models.Model) of the class from where it is called.

        :return: _description_ list of subclasses of cls that are instances of models.Model.
        :rtype: _type_ list
        """
        submodels = set()
        for model in cls.__subclasses__():
            if issubclass(model, models.Model):
                submodels.add(model)
                if model.__subclasses__():
                    res = model.get_submodels()
                    [submodels.add(el) for el in res]
        return list(submodels)

    @classmethod
    def get_leaf_models(cls):
        """
        _summary_ Recursive class-method that returns a list of all leaf models of cls - models in the class hierarchy that have no submodels themselves.
        If we don't allow ontologies to subclass models defined outside the core model hierarchy (i.e. not allowing an ontology model to subclass another ontology model), then 
        this approach will speed up some lookup functionality of child instances across the unified id-space defined in RootModel.
        If ontology models inherit from one another, than the actual model that an id in RootModel belongs to (was created in) could be in the parent model of the ontology model that inherits from the other ontology model, i.e. searching in the leaf models would not be sufficient.

        :return: _description_
        :rtype: _type_
        """
        submodels = set()
        for model in cls.__subclasses__():
            if issubclass(model, models.Model):
                if model.__subclasses__():
                    res = model.get_leaf_models()
                    if res:
                        [submodels.add(el) for el in res]
                else:
                    submodels.add(model)
        return submodels

    @classmethod
    def get_model_of_instance_id(cls, instance_id):
        """
        Helper method that returns the actual model (submodel of RootModel) that an id residing in RootModel belongs to.

        :param instance_id: _description_
        :type instance_id: _type_
        :return: _description_
        :rtype: _type_
        """
        print("called get model from:", cls)
        # this logic here could be moved into a @property.getter called child_model_lookup; if it might be used by different methods
        if not RootModel._child_model_lookup:
            print("calculating model lookup")
            # using leaf models here only works under the condition outlined in the get_leaf_models method above. If we want to diverge from this, we got to use get_submodels and recursively traverse to the lowest model in the hierarchy where the id is found.
            leaf_models = RootModel.get_leaf_models()
            RootModel._child_model_lookup = {
                inst_id: child_model for child_model in leaf_models for inst_id in child_model.objects.values_list("id", flat=True)}
        else:
            print("fetched cached model_lookup without re-calculating it")
        return RootModel._child_model_lookup.get(instance_id)

    @classmethod
    def get_model_of_instance(cls, instance_id: "RootModel", root=None) -> "RootModel":
        """
        _summary_ This is the alternative implementation of get_model_of_instance_id, that searches in all submodels of RootModel, and returns the match furthest down in the hierarchy (which is the actual model the instance we search for by id lives in).
        This is just a dirty example that the logic works, there are cleaner implementations that use methods defined above and could also be written to cache the lookup like above.

        :param instance_id: _description_
        :type instance_id: RootModel
        :param root: _description_, defaults to None
        :type root: _type_, optional
        :return: _description_
        :rtype: RootModel
        """
        if not root:
            direct_submodels = cls.__subclasses__()
        else:
            direct_submodels = root.__subclasses__()

        model_id_lookup = {
            inst_id: child_model for child_model in direct_submodels for inst_id in child_model.objects.values_list("id", flat=True)}
        res = model_id_lookup.get(instance_id)
        higher_res = None
        for submodel in direct_submodels:
            higher_res = cls.get_model_of_instance(instance_id, root=submodel)
            if higher_res:
                break

        if higher_res:
            return higher_res
        else:
            return res

    @staticmethod
    def get_instance_by_id(root_model_id: int) -> "RootModel":
        """
        Helper method that returns the actual instance of the right submodel of RootModel that an id stored in RootModel belongs to.


        :param root_model_id: _description_
        :type root_model_id: int
        :return: _description_
        :rtype: RootModel
        """
        model = RootModel.get_model_of_instance_id(root_model_id)
        return model.objects.get(id=root_model_id)

    def save(self, *args, **kwargs):
        print(f"Called RootModel save method: {args=}, {kwargs=}")
        # if we create a new entity in of the child models, this save method will also be triggered (save method calls bubble up through the whole model-hierarchy)
        # creating a new instance of a child model necessitates the update of the child_model_lookup: this can be enforced by reseting it to a empty dict.
        # re-creation of the lookup is then enforced in the method that actually uses it
        # of course, this could be made even more performant by adding the newly created instance to the lookup instead of resetting the whole thing.
        print("reset rootmodel._child_model_lookup")
        RootModel._child_model_lookup = {}
        super().save(*args, **kwargs)


class RootEntity(RootModel):
    """
    _summary_ Class that serves as a baseclass for a subset of classes.  Implemented here to reflect the architecture we have in apis vanilla and apis rdf.

    :param RootModel: _description_
    :type RootModel: _type_
    """
    name = models.CharField("name", max_length=100, blank=False, null=False)

    rootentity_rootmodel_ptr = models.OneToOneField(
        RootModel, on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,

    )

    def __str__(self, *args, **kwargs):
        return f"<{self.__class__.__name__}: {self.name} ({self.id})>"

    def __repr__(self, *args, **kwargs):
        return self.__str__()

    def save(self, *args, **kwargs):
        print(f"Called RootEntity save method: {args=}, {kwargs=}")
        super().save(*args, **kwargs)


class Person(RootEntity):
    """
    _summary_ Blank implementation of a Person class without mixins.

    :param RootEntity: _description_
    :type RootEntity: _type_
    """
    first_name = models.CharField(
        "first_name", max_length=100, blank=False, null=False)
    person_rootentity_ptr = models.OneToOneField(
        RootEntity, on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,

    )

    def save(self, *args, **kwargs):
        print(f"Called Person save method: {args=}, {kwargs=}")
        super().save(*args, **kwargs)


class TempMixin(RootModel):
    """
    _summary_ The actual mixin. 

    :param RootModel: _description_
    :type RootModel: _type_
    """
    start_date_written = models.CharField(
        "start_date_written", max_length=100, blank=True, null=True)
    end_date_written = models.CharField(
        "end_date_written", max_length=100, blank=True, null=True)
    tempmixin_rootmodel_ptr = models.OneToOneField(
        RootModel, on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,

    )

    def save(self, *args, **kwargs):
        print(f"Called TempMixin save method: {args=}, {kwargs=}")
        print(f"{self.start_date_written=}")
        super().save(*args, **kwargs)


class StatementTemporalisationMixin(RootModel):
    """
    _summary_ Example of what kind of flexibility we gain by allowing different Mixins to be substituted by one another or to be added in addition to other mixins. This mixin could have a distinct semantic notion, that can be attached to it (on a class level, not instance level!): 
    f.e. That it denotes that the time when the statement was made (which is different from when the time that is captured within the statement). Example: Think of an instance of a Person Model that inherits both mixins: TempMixin and StatementTemporalisationMixin: TempMixin could express that a person lived from start to end, and this StatementTemporalisation...  residing in the same model could express
    that said statement (that the person lived from start to end) was itself uttered at a specific point in time.

    If we really wanted to limit the extend of the statmenttemporalisation to a specific statement within the inerhiting instance, we could add a field to StatementTemporalisatioMixin that takes the field names or a list of field names the mixin applies to (like f.e. the birth date of a person)
    This modelling approach would allow for things like provenance and detailed sources to be recorded where needed. Think of adding the person that uttered the temporalised statement as a field  like 'author' here, etc. 

    :param RootModel: _description_
    :type RootModel: _type_
    """
    statement_start = models.CharField(
        "start_date_written", max_length=100, blank=True, null=True)
    statement_end = models.CharField(
        "end_date_written", max_length=100, blank=True, null=True)
    statement_temproalistaion_mixin_rootmodel_ptr = models.OneToOneField(
        RootModel, on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,

    )


class MixinPerson(TempMixin, StatementTemporalisationMixin, RootEntity):
    """
    _summary_ Seperate Implementation of a Person model, that includes the TempMixin and the StatementTemporalisation Mixin

    :param TempMixin: _description_
    :type TempMixin: _type_
    :param StatementTemporalisationMixin: _description_
    :type StatementTemporalisationMixin: _type_
    :param RootEntity: _description_
    :type RootEntity: _type_
    """
    first_name = models.CharField("first_name", max_length=50, null=True)
    mixinperson_rootentity_ptr = models.OneToOneField(
        RootEntity, on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,

    )

    def save(self, *args, **kwargs):
        print(f"Called MixinPerson save method: {args=}, {kwargs=}")
        print(f"{self.start_date_written=}")
        super().save(*args, **kwargs)


class TempWork(RootEntity, TempMixin):
    """
    _summary_ Redundant, just another example of using the TempMixin across models.

    :param RootEntity: _description_
    :type RootEntity: _type_
    :param TempMixin: _description_
    :type TempMixin: _type_
    """
    title = models.CharField("title", max_length=100, blank=False, null=False)
    author = models.ForeignKey(
        MixinPerson, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        print(f"Called TempWork save method: {args=}, {kwargs=}")
        super().save(*args, **kwargs)
