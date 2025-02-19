from fastapi import HTTPException
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from controllers.BaseController import BaseController
from models import BlogModel, BlogDeleteModel, BlogEditModel, BlogResponse, CommonResponse
from database import Blog
from fastapi import Header, HTTPException

class BlogController(BaseController):

    def setup(self):
        app = self.app
        
        @app.post("/blogs/", response_model=CommonResponse)
        async def create_blog(blog: BlogModel, API_KEY: str = Header(...)):
            return self.create_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/edit/", response_model=CommonResponse)
        async def edit_blog(blog: BlogEditModel, API_KEY: str = Header(...)):
            return self.edit_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/delete/", response_model=CommonResponse)
        async def delete_blog(blog: BlogDeleteModel, API_KEY: str = Header(...)):
            return self.delete_blog(blog=blog, access_token=API_KEY)
        
        @app.post("/blogs/user/{user_id}", response_model=CommonResponse)
        async def get_blogs_by_user(user_id: int):
            return self.get_blogs_by_user(user_id=user_id)
        
        @app.post("/blogs/{blog_id}", response_model=CommonResponse)
        async def get_blog_by_id(blog_id: int):
            return self.get_blog_handler(blog_id=blog_id)
        
        @app.post("/all_blogs/", response_model=CommonResponse)
        async def get_blogs():
            return self.get_blogs()

    def create_blog(self, blog: BlogModel, access_token: str):
        session = self.manager.Session()
        try:
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            new_blog = Blog(
                user_id=blog.user_id,
                title=blog.title,
                content=blog.content,
                created_at=datetime.now()
            )
            session.add(new_blog)
            session.commit()
            
            return CommonResponse(
                message="Blog created successfully",
                data=BlogResponse(
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

    def edit_blog(self, blog: BlogResponse, access_token: str):
        session = self.manager.Session()
        try:
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            if not user:
                self.raise_401()
            existing_blog = session.query(Blog).filter(Blog.id == blog.id).first()
            if not existing_blog:
                self.raise_404()
            existing_blog.title = blog.title
            existing_blog.content = blog.content
            existing_blog.created_at = datetime.now()
            session.commit()
            return CommonResponse(
                message="Blog updated successfully",
                data=BlogResponse(
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

    def delete_blog(self, blog: BlogResponse, access_token: str):
        session = self.manager.Session()
        try:
            user = self.authenticate(user_id=blog.user_id, access_token=access_token, session=session)
            if not user:
                self.raise_401()
            existing_blog = session.query(Blog).filter(Blog.id == blog.id).first()
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
    
    def get_blogs(self):
        session = self.manager.Session()
        try:
            print("1")
            blogs = session.query(Blog).order_by(Blog.created_at.desc()).all()
            print("2")
            items = []
            for blog in blogs:
                items.append(
                    BlogResponse(
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

    def get_blogs_by_user(self, user_id: int):
        session = self.manager.Session()
        try:
            blogs = session.query(Blog).filter(Blog.user_id == user_id).order_by(Blog.created_at.desc()).all()
            items = []
            for blog in blogs:
                items.append(
                    BlogResponse(
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
            blog = session.query(Blog).filter(Blog.id == blog_id).first()
            if not blog:
                raise HTTPException(404, detail="Blog not found")
            return CommonResponse(
                message="Blog retrieved successfully",
                data=BlogResponse(
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