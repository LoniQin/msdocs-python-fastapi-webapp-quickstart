from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from controllers.BaseController import BaseController
from models import BlogModel, BlogV2DeleteModel, BlogV2EditModel, BlogV2Response, CommonResponse
from database import BlogV2, Blog
from fastapi import Header, HTTPException

class BlogV2Controller(BaseController):

    def setup(self):
        app = self.app

        # Uncomment this code to migrate
        #@app.get("/blogs_v2/migrate/", response_model=CommonResponse)
        #async def migrate_blog():
        #    return self.migrate_blog()
        
        @app.post("/blogs/v2/", response_model=CommonResponse)
        async def create_blog(blog: BlogModel, API_KEY: str = Header(...)):
            return self.create_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/v2/edit/", response_model=CommonResponse)
        async def edit_blog(blog: BlogV2EditModel, API_KEY: str = Header(...)):
            return self.edit_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/v2/delete/", response_model=CommonResponse)
        async def delete_blog(blog: BlogV2DeleteModel, API_KEY: str = Header(...)):
            return self.delete_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/v2/user/{user_id}", response_model=CommonResponse)
        async def get_blogs_by_user(user_id: int):
            return self.get_blogs_by_user(user_id=user_id)
        
        @app.post("/blogs/v2/{blog_id}", response_model=CommonResponse)
        async def get_blog_by_id(blog_id: int):
            return self.get_blog_handler(blog_id=blog_id)
        
    def migrate_blog(self):
        session = self.manager.Session()
        try:
            # Step 1: Query all blogs from the Blog table
            blogs = session.query(Blog).all()
            
            # Step 2: Create BlogV2 instances and add them to the session
            for blog in blogs:
                new_blog_v2 = BlogV2(
                    user_id=blog.user_id,
                    title=blog.title,
                    content=blog.content,
                    created_at=blog.created_at
                )
                session.add(new_blog_v2)

            # Step 3: Commit the session to save changes to the database
            session.commit()

            blogs_v2 = session.query(BlogV2).all()
             # Step 2: Create BlogV2 instances and add them to the session
            responses = []
            for blog in blogs_v2:
                new_blog_v2 = BlogV2Response(
                    id=blog.id, 
                    user_id=blog.user_id, 
                    title=blog.title, 
                    content=blog.content, 
                    created_at=blog.created_at
                )
                responses.append(new_blog_v2)
            
            return CommonResponse(
                message="Blog created successfully",
                data=responses
            )
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(400, detail="Database integrity error")
        except Exception as e:
            session.rollback()
            raise HTTPException(500, detail=str(e))
        finally:
            session.close()
        return CommonResponse(message='Migrate successfully', data={})

    def create_blog(self, blog: BlogModel, access_token: str):
        session = self.manager.Session()
        try:
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            if not user:
                self.raise_401()
            new_blog = BlogV2(
                user_id=blog.user_id,
                title=blog.title,
                content=blog.content,
                created_at=datetime.now()
            )
            session.add(new_blog)
            session.commit()
            
            return CommonResponse(
                message="Blog created successfully",
                data=BlogV2Response(
                    id=new_blog.id,
                    user_id=new_blog.user_id,
                    title=new_blog.title,
                    content=new_blog.content,
                    created_at=new_blog.created_at
                )
            )
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(400, detail="Database integrity error")
        except Exception as e:
            session.rollback()
            raise HTTPException(500, detail=str(e))
        finally:
            session.close()

    def edit_blog(self, blog: BlogV2Response, access_token: str):
        session = self.manager.Session()
        try:
            print(1)
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            if not user:
                self.raise_401()
            print(2)
            existing_blog = session.query(BlogV2).filter(BlogV2.id == blog.id).first()
            if not existing_blog:
                self.raise_404()
            print(3)
            existing_blog.title = blog.title
            existing_blog.content = blog.content
            existing_blog.created_at = datetime.now()
            print(4)
            session.commit()
            print(5)
            return CommonResponse(
                message="Blog updated successfully",
                data=BlogV2Response(
                    id=existing_blog.id,
                    user_id=existing_blog.user_id,
                    title=existing_blog.title,
                    content=existing_blog.content,
                    created_at=existing_blog.created_at
                )
            )
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(400, detail="Database integrity error")
        except Exception as e:
            session.rollback()
            raise HTTPException(500, detail=str(e))
        finally:
            print("Edit blog is executed.")
            session.close()

    def delete_blog(self, blog: BlogV2Response, access_token: str):
        session = self.manager.Session()
        try:
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            if not user:
                self.raise_401()
            existing_blog = session.query(BlogV2).filter(BlogV2.id == blog.id).first()
            if not existing_blog:
                self.raise_404()
            session.delete(existing_blog)  
            session.commit()           
            return CommonResponse(
                message="Blog deleted successfully",
                data=blog
            )
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(400, detail="Database integrity error")
        except Exception as e:
            session.rollback()
            raise HTTPException(500, detail=str(e))
        finally:
            print("delete_blog is executed.")
            session.close()

    def get_blogs_by_user(self, user_id: int):
        session = self.manager.Session()
        try:
            blogs = session.query(BlogV2).filter(BlogV2.user_id == user_id).order_by(BlogV2.created_at.desc()).all()
            items = []
            for blog in blogs:
                items.append(
                    BlogV2Response(
                        id=blog.id,
                        user_id=blog.user_id,
                        title=blog.title,
                        content=blog.content,
                        created_at=blog.created_at
                    )
                )
            if not blogs:
                raise HTTPException(404, detail="Blog not found")
            return CommonResponse(
                message="Blogs retrieved successfully",
                data=items
            )
        except Exception as e:
            raise HTTPException(500, detail=f"Server error: {str(e)}")
        finally:
            session.close()
    def get_blog_handler(self, blog_id: int):
        session = self.manager.Session()
        try:
            blog = session.query(BlogV2).filter(BlogV2.id == blog_id).first()
            if not blog:
                raise HTTPException(404, detail="Blog not found")
            return CommonResponse(
                message="Blog retrieved successfully",
                data=BlogV2Response(
                    id=blog.id,
                    user_id=blog.user_id,
                    title=blog.title,
                    content=blog.content,
                    created_at=blog.created_at
                )
            )
        except Exception as e:
            raise HTTPException(500, detail=f"Server error: {str(e)}")
        finally:
            session.close()