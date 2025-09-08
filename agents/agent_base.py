# agents/agent_base.py

import uuid
import datetime
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from config.company_profile import company_profile

class AgentBase(ABC):
    def __init__(self, name, department, role, memory=None, memory_manager=None, research_agent=None):
        self.agent_id = str(uuid.uuid4())
        self.name = name
        self.department = department
        self.role = role
        
        # Handle backward compatibility for memory parameter
        if memory_manager is not None:
            self.memory_manager = memory_manager
            self.memory = None  # Deprecated direct memory access
        elif memory is not None:
            # Backward compatibility: wrap old memory in a compatibility layer
            self.memory = memory
            self.memory_manager = None
        else:
            self.memory = None
            self.memory_manager = None
            
        self.research_agent = research_agent
        self.created_at = datetime.datetime.utcnow()
        
        # File management and session support
        self.file_manager = None
        self.session_manager = None
        self.current_mode = "persistent"  # Default mode

    def log(self, message: str):
        timestamp = datetime.datetime.utcnow().isoformat()
        print(f"[{self.name} | {self.role}] {timestamp} -> {message}")

    def save_to_memory(self, task: str, result: str):
        """ Store task-result pair to memory """
        if self.memory_manager:
            # Use centralized memory system
            metadata = {
                "task": task,
                "agent_name": self.name,
                "department": self.department,
                "role": self.role,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
            return self.memory_manager.store_data(
                agent_id=self.agent_id,
                data_type="task_result",
                content=f"Task: {task}\nResult: {result}",
                metadata=metadata
            )
        elif self.memory:
            # Backward compatibility with old memory system
            return self.memory.store(agent_id=self.agent_id, task=task, result=result)
        else:
            self.log("Warning: No memory system available for storing data")
            return {"status": "no_memory", "message": "No memory system configured"}

    def retrieve_memory(self, query: str, top_k: int = 3):
        """ Fetch similar past memory"""
        if self.memory_manager:
            # Use centralized memory system
            filters = {
                "agent_id": self.agent_id,
                "data_type": "task_result"
            }
            result = self.memory_manager.retrieve_data(
                agent_id=self.agent_id,
                query=query,
                data_type="task_result",
                filters=filters
            )
            
            # Extract results for backward compatibility
            if result.get("status") == "success":
                return result.get("results", [])[:top_k]
            else:
                self.log(f"Memory retrieval failed: {result.get('message', 'Unknown error')}")
                return []
        elif self.memory:
            # Backward compatibility with old memory system
            return self.memory.search(agent_id=self.agent_id, query=query, top_k=top_k)
        else:
            self.log("Warning: No memory system available for retrieving data")
            return []

    def request_permission(self, task_description: str):
        """ Stub for user approval – override with actual logic later """
        self.log(f"Requesting user approval for: {task_description}")
        return True  # Always approved for now (simulate interactive permission)

    def get_company_context(self):
        """Get company profile context"""
        return company_profile.get_context()

    async def request_research(self, research_query: str):
        """Request research from the centralized research agent"""
        if self.research_agent:
            self.log(f"🔍 Requesting research: {research_query}")
            research_result = await self.research_agent.execute_task(research_query)
            return research_result
        else:
            self.log("⚠️ No research agent available")
            return "Research service not available"

    @abstractmethod
    async def execute_task(self, task: str):
        """ Agents must define their task handler """
        pass

    def send_message_to(self, receiver_name: str, message: str):
        """Stub for sending a message to another agent. Should be overridden or connected to the system's messaging infrastructure."""
        self.log(f"🔔 Signaling {receiver_name} via message_sent_event.")
        # Integrate with actual messaging/event system here
    
    # Additional memory system methods for centralized memory integration
    
    def log_conversation(self, conversation_thread: list):
        """Log conversation thread to centralized memory system"""
        if self.memory_manager:
            return self.memory_manager.log_conversation(self.agent_id, conversation_thread)
        else:
            self.log("Warning: No memory manager available for conversation logging")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    def log_action(self, action: str, context: dict = None, result: str = None):
        """Log action to centralized memory system"""
        if self.memory_manager:
            return self.memory_manager.log_action(self.agent_id, action, context, result)
        else:
            self.log("Warning: No memory manager available for action logging")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    def get_agent_history(self, limit: int = 10, filters: dict = None):
        """Get agent history from centralized memory system"""
        if self.memory_manager:
            return self.memory_manager.get_agent_history(self.agent_id, limit, filters)
        else:
            self.log("Warning: No memory manager available for history retrieval")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    def get_learning_insights(self, task_type: str = None):
        """Get learning insights from centralized memory system"""
        if self.memory_manager:
            return self.memory_manager.get_learning_insights(self.agent_id, task_type)
        else:
            self.log("Warning: No memory manager available for learning insights")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    def store_knowledge(self, content: str, data_type: str = "unstructured", metadata: dict = None):
        """Store knowledge to centralized memory system"""
        if self.memory_manager:
            if metadata is None:
                metadata = {}
            metadata.update({
                "agent_name": self.name,
                "department": self.department,
                "role": self.role,
                "timestamp": datetime.datetime.utcnow().isoformat()
            })
            return self.memory_manager.store_data(
                agent_id=self.agent_id,
                data_type=data_type,
                content=content,
                metadata=metadata
            )
        else:
            self.log("Warning: No memory manager available for knowledge storage")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    def search_knowledge(self, query: str, top_k: int = 5, filters: dict = None):
        """Search knowledge using similarity search in centralized memory system"""
        if self.memory_manager:
            if filters is None:
                filters = {}
            filters["agent_id"] = self.agent_id
            return self.memory_manager.search_similar(query, top_k, filters)
        else:
            self.log("Warning: No memory manager available for knowledge search")
            return {"status": "no_memory_manager", "message": "No memory manager configured"}
    
    # File Management Methods
    
    def set_file_manager(self, file_manager):
        """Set file manager for this agent"""
        self.file_manager = file_manager
    
    def set_session_manager(self, session_manager):
        """Set session manager for this agent"""
        self.session_manager = session_manager
    
    def set_mode(self, mode: str):
        """Set operating mode (persistent or oneshot)"""
        self.current_mode = mode
    
    def get_mode(self) -> str:
        """Get current operating mode"""
        return self.current_mode
    
    def should_use_memory(self) -> bool:
        """Determine if agent should use persistent memory based on mode"""
        return self.current_mode == "persistent"
    
    def save_output_file(self, content: Any, filename: str, category: str) -> Optional[str]:
        """Save output file using file manager"""
        if not self.file_manager:
            self.log("Warning: No file manager available for saving files")
            return None
        
        try:
            # Convert content to bytes if it's a string
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            else:
                # For other types, convert to JSON string then bytes
                import json
                content_bytes = json.dumps(content, indent=2).encode('utf-8')
            
            file_path = self.file_manager.save_file(
                content=content_bytes,
                filename=filename,
                category=category,
                agent_name=self.name
            )
            
            self.log(f"Saved file: {filename} to {category} category")
            
            # Add department to session if session manager is available
            if self.session_manager and hasattr(self.session_manager, 'current_session'):
                if self.session_manager.current_session:
                    self.session_manager.add_department_to_session(
                        self.session_manager.current_session.id,
                        self.department
                    )
            
            return file_path
            
        except Exception as e:
            self.log(f"Error saving file {filename}: {str(e)}")
            return None
    
    def get_output_file_path(self, filename: str, category: str) -> Optional[str]:
        """Get path for output file"""
        if not self.file_manager:
            return None
        
        try:
            return self.file_manager.get_file_path(filename, category)
        except Exception as e:
            self.log(f"Error getting file path for {filename}: {str(e)}")
            return None
    
    def list_agent_files(self) -> list:
        """List all files created by this agent in current session"""
        if not self.file_manager:
            return []
        
        try:
            all_files = self.file_manager.list_session_files()
            # Filter files created by this agent (if logged in file operations)
            return all_files  # For now, return all files
        except Exception as e:
            self.log(f"Error listing agent files: {str(e)}")
            return []
    
    def create_document(self, content: Dict[str, Any], doc_type: str, filename: str) -> Optional[str]:
        """Create document using document generator"""
        try:
            from utils.document_generator import DocumentGenerator
            
            doc_gen = DocumentGenerator()
            
            if doc_type.lower() == 'docx':
                doc_bytes = doc_gen.create_docx(content)
                if not filename.endswith('.docx'):
                    filename += '.docx'
            elif doc_type.lower() == 'pptx':
                doc_bytes = doc_gen.create_pptx(content.get('slides', []))
                if not filename.endswith('.pptx'):
                    filename += '.pptx'
            elif doc_type.lower() == 'xlsx':
                doc_bytes = doc_gen.create_xlsx(content)
                if not filename.endswith('.xlsx'):
                    filename += '.xlsx'
            elif doc_type.lower() == 'pdf':
                doc_bytes = doc_gen.create_pdf(content)
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
            else:
                raise ValueError(f"Unsupported document type: {doc_type}")
            
            # Determine category based on document type and agent department
            if self.department.lower() in ['rnd', 'r&d', 'research']:
                category = 'reports'
            elif self.department.lower() in ['marketing', 'sales']:
                category = 'docs'
            elif self.department.lower() in ['finance', 'accounting']:
                category = 'reports'
            else:
                category = 'docs'
            
            return self.save_output_file(doc_bytes, filename, category)
            
        except ImportError:
            self.log("Document generator not available. Install required dependencies.")
            return None
        except Exception as e:
            self.log(f"Error creating document: {str(e)}")
            return None
    
    def create_code_project(self, spec: Dict[str, Any], project_type: str) -> Optional[Dict[str, str]]:
        """Create code project using code generator"""
        try:
            from utils.code_generator import CodeGenerator
            
            code_gen = CodeGenerator()
            files = code_gen.create_project_structure(project_type, spec)
            
            saved_files = {}
            for filename, content in files.items():
                file_path = self.save_output_file(content, filename, 'code')
                if file_path:
                    saved_files[filename] = file_path
            
            self.log(f"Created {len(saved_files)} code files for {project_type} project")
            return saved_files
            
        except ImportError:
            self.log("Code generator not available. Install required dependencies.")
            return None
        except Exception as e:
            self.log(f"Error creating code project: {str(e)}")
            return None