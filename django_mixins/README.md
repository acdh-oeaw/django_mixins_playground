# Django Mixins

Playground project to test implementation of model class mixins in django.

# Reasoning

- mixins allow to share fields and methods across models at any point in the inheritance-hierarchy
- this allows for grouping functionality
- and deduplicating code. See apis-vanilla for an example where we could have used mixins: Look at TempEntityClass  in apis_metainfo and the fields it defines and then look at the Label-model in apis_vocabularies
- also, mixins facilitate to be precise about their semantics
- semantically different versions of similiar functionality can be implemented
- this allows to use two different implementations of a similiar mixin in two models that live on the same level of the model hierarchy

```python


# f.e. Consider Apis Vanilla (PSEUDO CODE)

###### Direct Inheritance

class TempEntityClass:
	name
	start_date_written
	end_date_written

# on the same level in the inheritance as Institution
class Person(TempEntityClass):
	#--> inherits start_date_written and end_date_written

# on the same level in the inheritance as Person
class Institution(TempEntityClass):
	#--> inhertis the same fields


#### Mixin Inheritance #####

# remove date fields from root class:
class TempEntityClass:
	name

# create one temporal mixin
class LifespanMixin:
	date_of_birth
	date_of_death

# create a second version with different semantics
class FoundingMixin:
	# yeah, example is a bit silly and not practical, but you get the idea
	founding_date
	shutdown_date

# use mixin 1
class Person(TempEntityClass, LifespanMixin):
	date_of_birth
	date_of_death

# use mixin 2
class Institution(TempEntityClass, FoundingMixin):
	founding_date
	shutdown_date

# use mixin 1 again
class Association(TempEntityClass, FoundingMixin):
	founding_date
	shutdown_date

# Note that FoundingMixin and LifespanMixin can each have their own parsers, handling methods, etc. It's not only about renaming fields.
```

# Findings

- mixins work exactly the same way as normal inheritance / multiple inheritance
- there is nothing syntactically or programmatically special about them
- it might be especially useful that the fields defined in the mixin reside within the mixin, even if they are inherited by models that implement the mixin
  - special functionality needed to manage the fields can be added to the mixins save() method, f.e. for date parsing, like we did in the TempEntityClasses save method in apis-vanilla
  - so there is only one implementation needed, and the implemantation of the parser could also be shared between multiple mixins
- Mixins lead to multiple inheritance (a class inheriting from more than one superclass)
- this has implications in django (see multiple inheritance below)

# Multiple Inheritance and Mixins

- In the models.py I implemented a common base model that functions as manages all ids across all other models
- this means that each model inherits the id field
- in the case of multiple inheritance, this means that inherited id fields clash within the model with multiple superclasses
- this can be resolved by explicitly creating the one-to-one field that django normally auto-creates to create a link between models that are bound by inheritance
- it should be never necessary to access these fields directly, they are needed for djangos background joins, etc.
- it should only be necessary to implement these fields in the core models, i.e. they could be left out in the ontology models, as long as ontology models are not allowed to inherit from one another (than the auto craeted names from django will be unique anyway)
- it would still be fine, if ontology models inherit from multiple core models (as long as all core models have these distinct explicit link fields)


# ID Example

As we shortly discussed the benefits of creating a unique ID space by creating a common base model for all other models, and as this specifically interferes with the multiple inheritance issue outlined above, I implemented example lookup functions that show that the inheritance tree can still be traversed easily, and an id visible in the root model can still be correctly attributed to the model class where it actually was defined. 

- see the ID lookup notebook for examples
