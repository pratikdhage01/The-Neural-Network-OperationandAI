/**
 * API client for communicating with the MSME Agent Server
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
        ...options,
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

// Chat API
export const chatAPI = {
    sendConsumerMessage: (message: string, conversationId?: string) =>
        fetchAPI<ChatResponse>('/api/chat/consumer', {
            method: 'POST',
            body: JSON.stringify({ message, conversation_id: conversationId }),
        }),

    sendSupplierMessage: (supplierId: string, message: string, conversationId?: string) =>
        fetchAPI<ChatResponse>(`/api/chat/supplier/${supplierId}`, {
            method: 'POST',
            body: JSON.stringify({ message, conversation_id: conversationId }),
        }),

    getHistory: (conversationId: string) =>
        fetchAPI<Conversation>(`/api/chat/history/${conversationId}`),

    listConversations: (limit = 20, type?: string) =>
        fetchAPI<Conversation[]>(`/api/chat/conversations?limit=${limit}${type ? `&conversation_type=${type}` : ''}`),
};

// Orders API
export const ordersAPI = {
    list: (status?: string, limit = 50) =>
        fetchAPI<Order[]>(`/api/orders?limit=${limit}${status ? `&status=${status}` : ''}`),

    get: (orderId: string) =>
        fetchAPI<Order>(`/api/orders/${orderId}`),

    getStats: () =>
        fetchAPI<OrderStats>('/api/orders/stats'),

    updateStatus: (orderId: string, status: string) =>
        fetchAPI<{ message: string }>(`/api/orders/${orderId}/status?status=${status}`, {
            method: 'PUT',
        }),
};

// Inventory API
export const inventoryAPI = {
    list: (category?: string, lowStockOnly = false) =>
        fetchAPI<Product[]>(`/api/inventory?low_stock_only=${lowStockOnly}${category ? `&category=${category}` : ''}`),

    get: (productId: string) =>
        fetchAPI<Product>(`/api/inventory/${productId}`),

    getStats: () =>
        fetchAPI<InventoryStats>('/api/inventory/stats'),

    getLowStock: () =>
        fetchAPI<Product[]>('/api/inventory/low-stock'),

    updateStock: (productId: string, quantityChange: number) =>
        fetchAPI<{ message: string }>(`/api/inventory/${productId}/stock?quantity_change=${quantityChange}`, {
            method: 'PUT',
        }),
};

// Suppliers API
export const suppliersAPI = {
    list: (activeOnly = true) =>
        fetchAPI<Supplier[]>(`/api/suppliers?active_only=${activeOnly}`),

    get: (supplierId: string) =>
        fetchAPI<Supplier>(`/api/suppliers/${supplierId}`),

    getChatHistory: (supplierId: string) =>
        fetchAPI<Conversation[]>(`/api/suppliers/${supplierId}/chat`),

    getQueries: (supplierId: string, status?: string) =>
        fetchAPI<SupplierQuery[]>(`/api/suppliers/${supplierId}/queries${status ? `?status=${status}` : ''}`),
};

// Staff API
export const staffAPI = {
    list: () =>
        fetchAPI<Staff[]>('/api/staff'),

    get: (staffId: string) =>
        fetchAPI<Staff>(`/api/staff/${staffId}`),

    getWorkload: () =>
        fetchAPI<WorkloadDistribution[]>('/api/staff/workload'),

    assignTask: (staffId: string, description: string, orderId?: string) =>
        fetchAPI<{ task_id: string; message: string }>(`/api/staff/${staffId}/assign?description=${encodeURIComponent(description)}${orderId ? `&order_id=${orderId}` : ''}`, {
            method: 'POST',
        }),

    completeTask: (staffId: string, taskId: string) =>
        fetchAPI<{ message: string }>(`/api/staff/${staffId}/tasks/${taskId}/complete`, {
            method: 'PUT',
        }),
};

// Analytics API
export const analyticsAPI = {
    getOverview: () =>
        fetchAPI<DashboardStats>('/api/analytics/overview'),

    getBottlenecks: () =>
        fetchAPI<Bottleneck[]>('/api/analytics/bottlenecks'),

    analyzeBottlenecks: () =>
        fetchAPI<{ analysis: string; bottlenecks: Bottleneck[] }>('/api/analytics/bottlenecks/analyze'),

    getWorkload: () =>
        fetchAPI<{ distribution: WorkloadDistribution[]; summary: WorkloadSummary }>('/api/analytics/workload'),

    getAgentActivity: (limit = 50) =>
        fetchAPI<AgentActivity[]>(`/api/analytics/agent-activity?limit=${limit}`),

    getOrderTrends: (days = 7) =>
        fetchAPI<OrderTrend[]>(`/api/analytics/orders/trends?days=${days}`),

    getInventoryAlerts: () =>
        fetchAPI<{ out_of_stock: Product[]; low_stock: Product[] }>('/api/analytics/inventory/alerts'),

    resolveBottleneck: (bottleneckId: string) =>
        fetchAPI<{ message: string }>(`/api/analytics/bottlenecks/${bottleneckId}/resolve`, {
            method: 'PUT',
        }),
};

// Types
export interface ChatResponse {
    response: string;
    conversation_id: string;
    context: Record<string, unknown>;
}

export interface Message {
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
}

export interface Conversation {
    _id: string;
    conversation_id: string;
    type: 'consumer' | 'supplier';
    supplier_id?: string;
    messages: Message[];
    context: Record<string, unknown>;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface Order {
    _id: string;
    order_number: string;
    customer_info: {
        name: string;
        phone: string;
        email?: string;
        address: string;
        city: string;
        pincode: string;
    };
    items: OrderItem[];
    total_amount: number;
    status: string;
    assigned_staff_id?: string;
    created_at: string;
    updated_at: string;
    estimated_delivery?: string;
}

export interface OrderItem {
    product_id: string;
    product_name: string;
    quantity: number;
    unit_price: number;
    total_price: number;
}

export interface OrderStats {
    total: number;
    by_status: Record<string, number>;
    orders_today: number;
    revenue_today: number;
}

export interface Product {
    _id: string;
    name: string;
    category: string;
    description: string;
    price: number;
    quantity: number;
    low_stock_threshold: number;
    supplier_id?: string;
}

export interface InventoryStats {
    total_products: number;
    out_of_stock: number;
    low_stock: number;
    total_value: number;
    by_category: Record<string, { count: number; total_value: number }>;
}

export interface Supplier {
    _id: string;
    name: string;
    contact_person: string;
    phone: string;
    email: string;
    address: string;
    categories: string[];
    products_offered: string[];
    avg_response_time_hours: number;
    reliability_score: number;
    is_active: boolean;
}

export interface SupplierQuery {
    _id: string;
    supplier_id: string;
    product_name: string;
    quantity_needed: number;
    status: string;
    response?: string;
    created_at: string;
    responded_at?: string;
}

export interface Staff {
    _id: string;
    name: string;
    role: string;
    phone: string;
    email?: string;
    is_available: boolean;
    current_workload: number;
    max_workload: number;
    assigned_tasks: StaffTask[];
    skills: string[];
}

export interface StaffTask {
    task_id: string;
    description: string;
    order_id?: string;
    status: string;
    priority: number;
    assigned_at: string;
    completed_at?: string;
}

export interface WorkloadDistribution {
    staff_id: string;
    staff_name: string;
    role: string;
    current_tasks: number;
    max_capacity: number;
    utilization_percent: number;
}

export interface WorkloadSummary {
    average_utilization: number;
    max_utilization: number;
    min_utilization: number;
    total_staff: number;
}

export interface DashboardStats {
    total_orders: number;
    pending_orders: number;
    processing_orders: number;
    total_products: number;
    low_stock_count: number;
    active_bottlenecks: number;
    staff_utilization: number;
    orders_today: number;
}

export interface Bottleneck {
    _id: string;
    type: string;
    severity: string;
    title: string;
    description: string;
    affected_resources: string[];
    suggested_actions: string[];
    is_resolved: boolean;
    detected_at: string;
    resolved_at?: string;
}

export interface AgentActivity {
    _id: string;
    agent_name: string;
    action: string;
    details: string;
    conversation_id?: string;
    order_id?: string;
    timestamp: string;
    success: boolean;
}

export interface OrderTrend {
    date: string;
    orders: number;
    revenue: number;
}
