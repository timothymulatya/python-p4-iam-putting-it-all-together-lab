import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        
        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user first
            user = User(username="test_user")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            recipe = Recipe(
                    title="Delicious Shed Ham",
                    instructions="""Or kind rest bred with am shed then. In""" + \
                        """ raptures building an bringing be. Elderly is detract""" + \
                        """ tedious assured private so to visited. Do travelling""" + \
                        """ companions contrasted it. Mistress strongly remember""" + \
                        """ up to. Ham him compass you proceed calling detract.""" + \
                        """ Better of always missed we person mr. September""" + \
                        """ smallness northward situation few her certainty""" + \
                        """ something.""",
                    minutes_to_complete=60,
                    user_id=user.id  # Associate with the user
                    )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something."""
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user first
            user = User(username="test_user2")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            # Create a recipe with valid instructions (over 50 chars) but no title
            recipe = Recipe(
                instructions="This is a very long instruction that is definitely more than fifty characters long to pass validation.",
                minutes_to_complete=30,
                user_id=user.id
                # title is intentionally omitted
            )
            
            # We expect either an IntegrityError from the database or a ValueError from our validation
            with pytest.raises((IntegrityError, ValueError)):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_instructions_length(self):
        '''requires instructions to be at least 50 characters long.'''
        
        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user first
            user = User(username="test_user3")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            # Try to create a recipe with short instructions
            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol",  # Too short - less than 50 chars
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()

    def test_requires_instructions_present(self):
        '''requires instructions to be present.'''
        
        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user first
            user = User(username="test_user4")
            user.password_hash = "password123"
            db.session.add(user)
            db.session.commit()

            # Try to create a recipe with no instructions
            with pytest.raises((IntegrityError, ValueError)):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="",  # Empty instructions
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()