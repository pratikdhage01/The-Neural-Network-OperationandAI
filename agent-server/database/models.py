"""
Pydantic models for database collections.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v, info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")


# ============ ENUMS ============

class ProductCategory(str, Enum):
    JEWELRY = "jewelry"
    KITCHEN_APPLIANCES = "kitchen_appliances"
    MAKEUP = "makeup"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    AWAITING_STOCK = "awaiting_stock"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class BottleneckSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BottleneckType(str, Enum):
    INVENTORY_SHORTAGE = "inventory_shortage"
    WORKLOAD_IMBALANCE = "workload_imbalance"
    SUPPLIER_DELAY = "supplier_delay"
    ORDER_BACKLOG = "order_backlog"
    STAFF_UNAVAILABLE = "staff_unavailable"


class ConversationType(str, Enum):
    CONSUMER = "consumer"
    SUPPLIER = "supplier"


class SupplierQueryStatus(str, Enum):
    PENDING = "pending"
    RESPONDED_AVAILABLE = "available"
    RESPONDED_UNAVAILABLE = "unavailable"
    EXPIRED = "expired"


# ============ MODELS ============

class Product(BaseModel):
    """Product in inventory."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: ProductCategory
    description: str
    price: float
    quantity: int
    low_stock_threshold: int = 5
    supplier_id: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ProductCreate(BaseModel):
    """Schema for creating a product."""
    name: str
    category: ProductCategory
    description: str
    price: float
    quantity: int
    low_stock_threshold: int = 5
    supplier_id: Optional[str] = None
    image_url: Optional[str] = None


class OrderItem(BaseModel):
    """Item in an order."""
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float


class CustomerInfo(BaseModel):
    """Customer information for an order."""
    name: str
    phone: str
    email: Optional[str] = None
    address: str
    city: str
    pincode: str
    notes: Optional[str] = None


class Order(BaseModel):
    """Customer order."""
    id: Optional[str] = Field(default=None, alias="_id")
    order_number: str
    customer_info: CustomerInfo
    items: list[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    assigned_staff_id: Optional[str] = None
    conversation_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_delivery: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Supplier(BaseModel):
    """Supplier information."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    contact_person: str
    phone: str
    email: str
    address: str
    categories: list[ProductCategory]
    products_offered: list[str] = []
    avg_response_time_hours: float = 24.0
    reliability_score: float = 0.8
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SupplierCreate(BaseModel):
    """Schema for creating a supplier."""
    name: str
    contact_person: str
    phone: str
    email: str
    address: str
    categories: list[ProductCategory]
    products_offered: list[str] = []


class StaffTask(BaseModel):
    """Task assigned to staff."""
    task_id: str
    description: str
    order_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class Staff(BaseModel):
    """Staff member."""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    role: str
    phone: str
    email: Optional[str] = None
    is_available: bool = True
    current_workload: int = 0
    max_workload: int = 10
    assigned_tasks: list[StaffTask] = []
    skills: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class StaffCreate(BaseModel):
    """Schema for creating staff."""
    name: str
    role: str
    phone: str
    email: Optional[str] = None
    max_workload: int = 10
    skills: list[str] = []


class Message(BaseModel):
    """Chat message."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = {}


class Conversation(BaseModel):
    """Conversation session."""
    id: Optional[str] = Field(default=None, alias="_id")
    type: ConversationType
    supplier_id: Optional[str] = None
    customer_phone: Optional[str] = None
    messages: list[Message] = []
    context: dict = {}
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class BottleneckEvent(BaseModel):
    """Operational bottleneck event."""
    id: Optional[str] = Field(default=None, alias="_id")
    type: BottleneckType
    severity: BottleneckSeverity
    title: str
    description: str
    affected_resources: list[str] = []
    suggested_actions: list[str] = []
    is_resolved: bool = False
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AgentActivity(BaseModel):
    """Record of agent activity."""
    id: Optional[str] = Field(default=None, alias="_id")
    agent_name: str
    action: str
    details: str
    conversation_id: Optional[str] = None
    order_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None
    success: bool = True
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SupplierQuery(BaseModel):
    """Query sent to supplier for stock availability."""
    id: Optional[str] = Field(default=None, alias="_id")
    query_id: str  # Unique ID for this query
    order_id: str  # The order that triggered this query
    order_number: str
    supplier_id: str
    supplier_name: str
    product_id: str
    product_name: str
    product_category: str
    quantity_needed: int
    conversation_id: str  # Original consumer conversation
    status: SupplierQueryStatus = SupplierQueryStatus.PENDING
    response_quantity: Optional[int] = None
    response_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    responded_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ============ API RESPONSE MODELS ============

class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    response: str
    conversation_id: str
    context: dict = {}


class SupplierChatRequest(BaseModel):
    """Request for supplier chat."""
    message: str
    conversation_id: Optional[str] = None


class DashboardStats(BaseModel):
    """Dashboard overview statistics."""
    total_orders: int
    pending_orders: int
    processing_orders: int
    total_products: int
    low_stock_count: int
    active_bottlenecks: int
    staff_utilization: float
    orders_today: int


class WorkloadDistribution(BaseModel):
    """Staff workload distribution."""
    staff_id: str
    staff_name: str
    role: str
    current_tasks: int
    max_capacity: int
    utilization_percent: float


class SupplierResponseRequest(BaseModel):
    """Request from supplier responding to a stock query."""
    query_id: str
    available: bool
    quantity_available: Optional[int] = None
    message: Optional[str] = None
    estimated_days: Optional[int] = None
