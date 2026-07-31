(() => {
  "use strict";

  const API_BASE = (window.STOREFLOW_CONFIG?.apiBase || "http://localhost:8001/api/v1").replace(/\/$/, "");
  const TOKEN_KEY = "storeflow_access_token";
  const app = document.getElementById("app");
  const modalRoot = document.getElementById("modal-root");
  const toastRoot = document.getElementById("toast-root");

  const icons = {
    logo: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M5 8h14l-1 12H6L5 8Z"/><path d="M8 8a4 4 0 0 1 8 0"/><path d="M9 13h6M9 16h4"/></svg>`,
    dashboard: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="4" rx="1"/><rect x="14" y="11" width="7" height="10" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>`,
    products: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m12 3 8 4.5-8 4.5-8-4.5L12 3Z"/><path d="m4 12 8 4.5 8-4.5M4 16.5l8 4.5 8-4.5"/></svg>`,
    inventory: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 7.5 12 3l8 4.5v9L12 21l-8-4.5v-9Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/></svg>`,
    upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 16V4m0 0L7 9m5-5 5 5"/><path d="M4 15v4a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-4"/></svg>`,
    sparkles: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m12 3 1.3 3.7L17 8l-3.7 1.3L12 13l-1.3-3.7L7 8l3.7-1.3L12 3Z"/><path d="m18 14 .8 2.2L21 17l-2.2.8L18 20l-.8-2.2L15 17l2.2-.8L18 14ZM5 13l.8 2.2L8 16l-2.2.8L5 19l-.8-2.2L2 16l2.2-.8L5 13Z"/></svg>`,
    orders: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 3h10v4H7z"/><path d="M6 5H4v16h16V5h-2M8 12h8M8 16h5"/></svg>`,
    search: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg>`,
    plus: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 5v14M5 12h14"/></svg>`,
    refresh: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M20 7h-5V2"/><path d="M20 7a8 8 0 1 0 1 6"/></svg>`,
    alert: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 3 2.5 20h19L12 3Z"/><path d="M12 9v5m0 3h.01"/></svg>`,
    dollar: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/><path d="M15 8.5c-.7-.7-1.7-1-3-1-1.7 0-3 .8-3 2s1 1.8 3 2.2 3 1.1 3 2.4-1.3 2.4-3 2.4c-1.3 0-2.5-.4-3.3-1.3M12 5.5v13"/></svg>`,
    box: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 7.5 12 3l8 4.5v9L12 21l-8-4.5v-9Z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/></svg>`,
    check: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m5 12 4 4L19 6"/></svg>`,
    clock: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>`,
    menu: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 7h16M4 12h16M4 17h16"/></svg>`,
    info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-9h.01"/></svg>`,
    download: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 4v11m0 0 4-4m-4 4-4-4"/><path d="M5 20h14"/></svg>`,
    edit: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="m14 5 5 5L9 20H4v-5L14 5Z"/><path d="m12 7 5 5"/></svg>`,
    receive: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 8h16v12H4zM7 4h10l3 4H4l3-4Z"/><path d="M12 11v6m0 0 3-3m-3 3-3-3"/></svg>`,
    logout: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M10 5H5v14h5M14 8l4 4-4 4M8 12h10"/></svg>`,
    reset: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 12a8 8 0 1 0 2.3-5.7L4 8.5M4 4v4.5h4.5"/></svg>`,
  };

  const icon = (name) => `<span class="nav-icon">${icons[name] || icons.box}</span>`;
  let auth = {
    token: sessionStorage.getItem(TOKEN_KEY),
    user: null,
  };
  let state = {
    suppliers: [], products: [], salesDaily: [], inventoryTransactions: [],
    recommendations: [], purchaseOrders: [], activity: [], dashboard: null,
  };
  let productQuery = "";
  let categoryFilter = "All";
  let inventoryFilter = "All";
  let importPreview = null;
  let pendingImportFile = null;
  let initialLoading = true;
  let apiError = null;

  function clearSession() {
    sessionStorage.removeItem(TOKEN_KEY);
    auth = { token: null, user: null };
  }

  async function apiFetch(path, options = {}, requireAuth = true) {
    const headers = new Headers(options.headers || {});
    if (requireAuth && auth.token) headers.set("Authorization", `Bearer ${auth.token}`);
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const contentType = response.headers.get("content-type") || "";
    let body = null;
    if (contentType.includes("application/json")) body = await response.json();
    else if (response.status !== 204) body = await response.text();
    if (!response.ok) {
      if (response.status === 401 && requireAuth) {
        clearSession();
        apiError = null;
        initialLoading = false;
        render();
      }
      const detail = body?.detail || body?.message || body || `Request failed with status ${response.status}`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }
    return body;
  }

  const mapSupplier = (supplier) => ({
    id: supplier.id, name: supplier.name, email: supplier.email, phone: supplier.phone,
    deliveryDays: supplier.delivery_days, minimumOrder: Number(supplier.minimum_order_amount || 0),
  });

  const mapRecommendation = (recommendation) => ({
    id: recommendation.id, generationId: recommendation.generation_id,
    productId: recommendation.product_id, currentStock: recommendation.current_stock,
    averageDailySales: Number(recommendation.average_daily_sales), coverageDays: recommendation.coverage_days,
    unitsOnOrder: recommendation.units_on_order,
    recommendedCases: recommendation.decided_cases ?? recommendation.recommended_cases,
    originalCases: recommendation.recommended_cases, reason: recommendation.reason,
    status: recommendation.status, generatedAt: recommendation.generated_at,
  });

  const mapPurchaseOrder = (order) => ({
    id: order.id, poNumber: order.po_number, supplierId: order.supplier_id,
    supplierName: order.supplier_name, status: order.status,
    estimatedTotal: Number(order.estimated_total), createdAt: order.created_at,
    approvedAt: order.approved_at, receivedAt: order.received_at,
    items: order.items.map((item) => ({
      id: item.id, productId: item.product_id, productName: item.product_name, sku: item.sku,
      cases: item.quantity_cases, quantityUnits: item.quantity_units, receivedUnits: item.received_units,
      unitsPerCase: item.quantity_cases ? item.quantity_units / item.quantity_cases : 0,
      unitCost: Number(item.unit_cost), lineTotal: Number(item.line_total),
    })),
  });

  function buildActivity(sales, orders) {
    const orderItems = orders.slice(0, 4).map((order) => ({
      id: `order-${order.id}`, type: "order",
      message: `${order.po_number} is ${order.status.toLowerCase().replaceAll("_", " ")}`,
      detail: `${order.supplier_name} · ${order.items.length} products`,
      createdAt: order.received_at || order.approved_at || order.created_at,
    }));
    const saleItems = sales.slice(0, 4).map((sale) => ({
      id: `sale-${sale.id}`, type: "import", message: `${sale.product_name} sale recorded`,
      detail: `${sale.quantity} units · ${money(sale.revenue)} · ${sale.source}`,
      createdAt: sale.sold_at,
    }));
    return [...orderItems, ...saleItems].sort((a,b) => String(b.createdAt).localeCompare(String(a.createdAt)));
  }

  async function refreshData({ showLoader = false, notify = false } = {}) {
    if (showLoader) { initialLoading = true; render(); }
    try {
      const [suppliersRaw, productsRaw, inventoryRaw, salesRaw, recommendationsRaw, ordersRaw, dashboardRaw] = await Promise.all([
        apiFetch("/suppliers"), apiFetch("/products"), apiFetch("/inventory"),
        apiFetch("/sales?limit=1000"), apiFetch("/recommendations"),
        apiFetch("/purchase-orders"), apiFetch("/analytics/dashboard"),
      ]);
      const inventoryByProduct = new Map(inventoryRaw.map((item) => [item.product_id, item]));
      state.suppliers = suppliersRaw.map(mapSupplier);
      state.products = productsRaw.map((product) => {
        const inventory = inventoryByProduct.get(product.id);
        return {
          id: product.id, sku: product.sku, barcode: product.barcode, name: product.name,
          category: product.category, supplierId: product.supplier_id,
          purchasePrice: Number(product.purchase_price), sellingPrice: Number(product.selling_price),
          unitsPerCase: product.units_per_case, stock: inventory?.current_stock ?? 0,
          reorderPoint: product.reorder_point, safetyStock: product.safety_stock,
          leadTimeDays: product.lead_time_days, active: product.is_active,
        };
      });
      state.salesDaily = salesRaw.map((sale) => ({
        id: sale.id, date: sale.sold_at.slice(0,10), soldAt: sale.sold_at,
        barcode: sale.barcode, quantity: sale.quantity, revenue: Number(sale.revenue),
      }));
      state.recommendations = recommendationsRaw.map(mapRecommendation);
      state.purchaseOrders = ordersRaw.map(mapPurchaseOrder);
      state.dashboard = dashboardRaw;
      state.activity = buildActivity(salesRaw, ordersRaw);
      apiError = null; initialLoading = false; render();
      if (notify) toast("Data refreshed", "The latest PostgreSQL data is now displayed.");
    } catch (error) {
      console.error(error); apiError = error.message; initialLoading = false; render();
    }
  }

  async function bootstrap() {
    initialLoading = true;
    render();
    if (!auth.token) {
      initialLoading = false;
      render();
      return;
    }
    try {
      auth.user = await apiFetch("/auth/me");
      await refreshData();
    } catch (error) {
      console.error(error);
      clearSession();
      apiError = null;
      initialLoading = false;
      render();
    }
  }

  async function signIn(email, password) {
    const result = await apiFetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }, false);
    auth.token = result.access_token;
    auth.user = result.user;
    sessionStorage.setItem(TOKEN_KEY, auth.token);
    apiError = null;
    await refreshData({ showLoader: true });
  }

  function signOut() {
    clearSession();
    state = { suppliers: [], products: [], salesDaily: [], inventoryTransactions: [], recommendations: [], purchaseOrders: [], activity: [], dashboard: null };
    importPreview = null;
    pendingImportFile = null;
    apiError = null;
    location.hash = "dashboard";
    render();
  }

  async function resetDemoData() {
    if (!window.confirm("Reset products, inventory, sales, recommendations, and purchase orders to the original demo dataset?")) return;
    try {
      const result = await apiFetch("/demo/reset", { method: "POST" });
      importPreview = null;
      pendingImportFile = null;
      await refreshData();
      toast("Demo data restored", `${result.products} products and ${result.sales} historical sales rows were loaded.`);
    } catch (error) {
      toast("Reset failed", error.message);
    }
  }

  function resetState() { refreshData({ showLoader: true, notify: true }); }

  function esc(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  const money = (value) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value || 0);
  const num = (value) => new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value || 0);
  const shortDate = (value) => new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(new Date(value + (String(value).length === 10 ? "T12:00:00" : "")));
  const dateTime = (value) => new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }).format(new Date(value));

  function todayISO() {
    return new Date().toISOString().slice(0, 10);
  }

  function route() {
    return (location.hash.replace("#", "") || "dashboard").split("?")[0];
  }

  const productEmoji = (category) => ({ Beverages: "🥤", Chips: "🥨", Candy: "🍬", Household: "🧻" }[category] || "📦");

  function supplierById(id) { return state.suppliers.find((supplier) => supplier.id === id); }
  function productById(id) { return state.products.find((product) => product.id === id); }
  function productByBarcode(barcode) { return state.products.find((product) => product.barcode === String(barcode)); }

  function stockStatus(product) {
    if (product.stock <= Math.max(2, Math.round(product.reorderPoint * 0.45))) return "critical";
    if (product.stock <= product.reorderPoint) return "low";
    return "healthy";
  }

  function statusLabel(status) {
    return ({ healthy: "Healthy", low: "Low stock", critical: "Critical" }[status] || status);
  }

  function statusBadge(status, label = statusLabel(status)) {
    return `<span class="badge badge-${esc(status.toLowerCase())}">${esc(label)}</span>`;
  }

  function recentSales(days = 7) {
    const latest = state.salesDaily.reduce((max, sale) => sale.date > max ? sale.date : max, "0000-00-00");
    const cutoffDate = new Date(latest + "T12:00:00");
    cutoffDate.setDate(cutoffDate.getDate() - (days - 1));
    const cutoff = cutoffDate.toISOString().slice(0, 10);
    return state.salesDaily.filter((sale) => sale.date >= cutoff && sale.date <= latest);
  }

  function productSales(product, days = 28) {
    const latest = state.salesDaily.reduce((max, sale) => sale.date > max ? sale.date : max, "0000-00-00");
    const cutoffDate = new Date(latest + "T12:00:00");
    cutoffDate.setDate(cutoffDate.getDate() - (days - 1));
    const cutoff = cutoffDate.toISOString().slice(0, 10);
    return state.salesDaily.filter((sale) => sale.barcode === product.barcode && sale.date >= cutoff && sale.date <= latest);
  }

  function averageDailySales(product, days = 28) {
    const quantity = productSales(product, days).reduce((sum, sale) => sum + Number(sale.quantity), 0);
    return quantity / days;
  }

  function dashboardMetrics() {
    if (state.dashboard) return {
      weeklyRevenue: Number(state.dashboard.weekly_revenue || 0),
      low: Number(state.dashboard.low_stock_products || 0),
      critical: Number(state.dashboard.critical_products || 0),
      inventoryValue: Number(state.dashboard.inventory_value || 0),
      pendingOrders: Number(state.dashboard.open_purchase_orders || 0),
    };
    return { weeklyRevenue: 0, low: 0, critical: 0, inventoryValue: 0, pendingOrders: 0 };
  }

  function navItem(name, label, iconName) {
    return `<a class="nav-item ${route() === name ? "active" : ""}" href="#${name}" data-close-sidebar>${icon(iconName)}<span>${label}</span></a>`;
  }

  function shell(content, title) {
    const user = auth.user || { full_name: "Store Owner", email: "", role: "owner" };
    const initials = user.full_name.split(/\s+/).filter(Boolean).slice(0, 2).map((part) => part[0]).join("").toUpperCase() || "SO";
    return `<div class="app-shell">
      <aside class="sidebar" id="sidebar">
        <div class="brand"><div class="brand-mark">${icons.logo}</div><div><div class="brand-name">StoreFlow</div><div class="brand-sub">Inventory intelligence</div></div></div>
        <div class="nav-label">Workspace</div>
        <nav class="nav-list">
          ${navItem("dashboard", "Dashboard", "dashboard")}
          ${navItem("products", "Products", "products")}
          ${navItem("inventory", "Inventory", "inventory")}
          ${navItem("sales", "Sales import", "upload")}
          ${navItem("recommendations", "Reorder engine", "sparkles")}
          ${navItem("orders", "Purchase orders", "orders")}
        </nav>
        <div class="sidebar-footer"><div class="demo-box"><strong><span class="connection-dot"></span> Secure backend</strong><p>Signed in as ${esc(user.email)}. Data is stored in PostgreSQL.</p><button class="btn btn-secondary btn-small btn-block" data-action="refresh-data">Refresh backend data</button><button class="btn btn-ghost-light btn-small btn-block" data-action="reset-demo">${icon("reset")} Reset demo data</button></div></div>
      </aside>
      <main class="main"><header class="topbar"><div class="topbar-left"><button class="mobile-menu" data-action="toggle-menu" aria-label="Open menu">${icons.menu}</button><div class="page-heading">${esc(title)}</div></div><div class="topbar-user"><div class="store-chip"><div class="store-avatar">${esc(initials)}</div><div><div class="store-name">${esc(user.full_name)}</div><div class="store-loc">${esc(user.role)} · Northside Corner Store</div></div></div><button class="icon-button" data-action="logout" aria-label="Sign out" title="Sign out">${icons.logout}</button></div></header><section class="content">${content}</section></main>
    </div>`;
  }

  function lineChartSVG() {
    const sales = recentSales(14);
    const byDay = {};
    sales.forEach((sale) => { byDay[sale.date] = (byDay[sale.date] || 0) + Number(sale.revenue); });
    const points = Object.entries(byDay).sort(([a], [b]) => a.localeCompare(b));
    if (!points.length) return "";
    const values = points.map(([, value]) => value);
    const min = Math.min(...values) * .92;
    const max = Math.max(...values) * 1.05;
    const coords = points.map(([, value], i) => {
      const x = 18 + (i / Math.max(1, points.length - 1)) * 564;
      const y = 165 - ((value - min) / Math.max(1, max - min)) * 135;
      return [x, y];
    });
    const line = coords.map((point) => point.join(",")).join(" ");
    const area = `18,176 ${line} 582,176`;
    const circles = coords.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="3" fill="#0e8f83" stroke="white" stroke-width="2"/>`).join("");
    return `<svg class="line-chart" viewBox="0 0 600 185" role="img" aria-label="Fourteen day revenue chart">
      <defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0e8f83" stop-opacity=".22"/><stop offset="1" stop-color="#0e8f83" stop-opacity="0"/></linearGradient></defs>
      <path d="M18 42H582 M18 88H582 M18 134H582 M18 176H582" stroke="#edf0f5" stroke-width="1"/>
      <polygon points="${area}" fill="url(#areaFill)"/>
      <polyline points="${line}" fill="none" stroke="#0e8f83" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      ${circles}
    </svg><div class="chart-label-row"><span>${shortDate(points[0][0])}</span><span>${shortDate(points[Math.floor(points.length / 2)][0])}</span><span>${shortDate(points[points.length - 1][0])}</span></div>`;
  }

  function dashboardView() {
    const metrics = dashboardMetrics();
    const lowProducts = state.products
      .filter((p) => ["low", "critical"].includes(stockStatus(p)))
      .sort((a, b) => a.stock / a.reorderPoint - b.stock / b.reorderPoint)
      .slice(0, 6);

    const categoryRevenue = Object.fromEntries((state.dashboard?.category_sales_30_days || []).map((item) => [item.category, Number(item.revenue)]));
    const maxCategory = Math.max(...Object.values(categoryRevenue), 1);
    const categoryBars = Object.entries(categoryRevenue).sort((a,b) => b[1]-a[1]).map(([category, value]) => `
      <div class="bar-row"><div class="bar-label">${esc(category)}</div><div class="bar-track"><div class="bar-fill" style="width:${Math.max(4, value / maxCategory * 100)}%"></div></div><div class="bar-value">${money(value)}</div></div>`).join("");

    return shell(`
      <div class="page-intro"><div><h1>Store operations overview</h1><p>Live inventory and ordering data from the StoreFlow backend.</p></div><div class="actions"><a class="btn btn-secondary" href="#sales">${icon("upload")} Import sales</a><a class="btn btn-primary" href="#recommendations">${icon("sparkles")} Generate reorders</a></div></div>
      <div class="grid kpi-grid">
        <div class="kpi-card"><div class="kpi-top"><div class="kpi-label">Weekly sales</div><div class="kpi-icon teal">${icons.dollar}</div></div><div class="kpi-value">${money(metrics.weeklyRevenue)}</div><div class="kpi-note"><strong>PostgreSQL</strong> · latest 7 days</div></div>
        <div class="kpi-card"><div class="kpi-top"><div class="kpi-label">Low-stock products</div><div class="kpi-icon amber">${icons.alert}</div></div><div class="kpi-value">${metrics.low}</div><div class="kpi-note">${metrics.critical} require immediate attention</div></div>
        <div class="kpi-card"><div class="kpi-top"><div class="kpi-label">Inventory value</div><div class="kpi-icon blue">${icons.box}</div></div><div class="kpi-value">${money(metrics.inventoryValue)}</div><div class="kpi-note">Based on wholesale cost</div></div>
        <div class="kpi-card"><div class="kpi-top"><div class="kpi-label">Open purchase orders</div><div class="kpi-icon red">${icons.orders}</div></div><div class="kpi-value">${metrics.pendingOrders}</div><div class="kpi-note">Draft or approved orders</div></div>
      </div>
      <div class="grid dashboard-grid">
        <section class="card"><div class="card-header"><div><h2>Sales trend</h2><p>Revenue across the latest 14 days</p></div><span class="badge badge-healthy">Live API</span></div><div class="card-body chart-wrap">${lineChartSVG()}</div></section>
        <section class="card"><div class="card-header"><div><h2>Sales by category</h2><p>Latest 30 days</p></div></div><div class="card-body category-bars">${categoryBars}</div></section>
      </div>
      <div class="grid bottom-grid">
        <section class="card"><div class="card-header"><div><h2>Products needing attention</h2><p>Prioritized by stock level versus reorder point</p></div><a href="#inventory" class="btn btn-secondary btn-small">View inventory</a></div>
          <div class="table-wrap"><table><thead><tr><th>Product</th><th>Status</th><th>Stock level</th><th>Avg. daily sales</th><th>Supplier</th></tr></thead><tbody>
          ${lowProducts.map((p) => { const status = stockStatus(p); const ratio = Math.min(100, p.stock / Math.max(p.reorderPoint, 1) * 100); return `<tr><td><div class="product-cell"><div class="product-thumb">${productEmoji(p.category)}</div><div><div class="product-name">${esc(p.name)}</div><div class="product-meta">${esc(p.sku)}</div></div></div></td><td>${statusBadge(status)}</td><td><div class="progress-stock"><div class="stock-numbers"><span>${p.stock} units</span><span>ROP ${p.reorderPoint}</span></div><div class="progress-track"><div class="progress-fill ${status}" style="width:${Math.max(3,ratio)}%"></div></div></div></td><td class="number">${num(averageDailySales(p))}</td><td class="muted">${esc(supplierById(p.supplierId)?.name || "—")}</td></tr>`; }).join("")}
          </tbody></table></div>
        </section>
        <section class="card"><div class="card-header"><div><h2>Recent activity</h2><p>Operational changes and imports</p></div></div><div class="card-body activity-list">
          ${state.activity.slice(0,6).map((item) => `<div class="activity-item"><div class="activity-icon">${item.type === "import" ? icons.upload : item.type === "order" ? icons.orders : icons.inventory}</div><div><div class="activity-title">${esc(item.message)}</div><div class="activity-detail">${esc(item.detail)}</div></div><div class="activity-time">${dateTime(item.createdAt)}</div></div>`).join("")}
        </div></section>
      </div>`, "Dashboard");
  }

  function filteredProducts() {
    return state.products.filter((p) => {
      const matchesQuery = !productQuery || [p.name, p.sku, p.barcode].some((v) => v.toLowerCase().includes(productQuery.toLowerCase()));
      const matchesCategory = categoryFilter === "All" || p.category === categoryFilter;
      return matchesQuery && matchesCategory;
    });
  }

  function productsView() {
    const products = filteredProducts();
    const categories = ["All", ...new Set(state.products.map((p) => p.category))];
    return shell(`
      <div class="page-intro"><div><h1>Product catalog</h1><p>Manage SKU, supplier, case-pack, and replenishment settings.</p></div><div class="actions"><button class="btn btn-primary" data-action="add-product">${icon("plus")} Add product</button></div></div>
      <section class="card">
        <div class="toolbar"><div class="search"><span class="search-icon">${icons.search}</span><input id="product-search" value="${esc(productQuery)}" placeholder="Search by product, SKU, or barcode" /></div><select id="category-filter" class="select">${categories.map(c => `<option ${c === categoryFilter ? "selected" : ""}>${esc(c)}</option>`).join("")}</select><span class="muted">${products.length} products</span></div>
        <div class="table-wrap"><table><thead><tr><th>Product</th><th>Category</th><th>Supplier</th><th>Sell price</th><th>Case pack</th><th>Reorder point</th><th>Stock</th><th></th></tr></thead><tbody>
          ${products.map((p) => `<tr><td><div class="product-cell"><div class="product-thumb">${productEmoji(p.category)}</div><div><div class="product-name">${esc(p.name)}</div><div class="product-meta">${esc(p.sku)} · ${esc(p.barcode)}</div></div></div></td><td>${esc(p.category)}</td><td class="muted">${esc(supplierById(p.supplierId)?.name || "—")}</td><td class="number">${money(p.sellingPrice)}</td><td>${p.unitsPerCase} units</td><td>${p.reorderPoint}</td><td>${statusBadge(stockStatus(p), `${p.stock} units`)}</td><td><button class="btn btn-secondary btn-small" data-action="edit-product" data-id="${p.id}">${icon("edit")} Edit</button></td></tr>`).join("")}
        </tbody></table></div>
      </section>`, "Products");
  }

  function inventoryView() {
    let products = state.products;
    if (inventoryFilter !== "All") products = products.filter((p) => stockStatus(p) === inventoryFilter.toLowerCase());
    return shell(`
      <div class="page-intro"><div><h1>Inventory</h1><p>Track quantity on hand and record every physical adjustment.</p></div><div class="actions"><button class="btn btn-secondary" data-action="record-adjustment">${icon("edit")} Record adjustment</button><button class="btn btn-primary" data-action="receive-stock">${icon("receive")} Receive stock</button></div></div>
      <div class="callout callout-info">${icons.info}<div><strong>Auditable inventory workflow</strong><p>Every receiving, damage, expiration, and manual correction creates a PostgreSQL inventory transaction.</p></div></div>
      <section class="card"><div class="toolbar"><select id="inventory-filter" class="select"><option ${inventoryFilter === "All" ? "selected" : ""}>All</option><option ${inventoryFilter === "Healthy" ? "selected" : ""}>Healthy</option><option ${inventoryFilter === "Low" ? "selected" : ""}>Low</option><option ${inventoryFilter === "Critical" ? "selected" : ""}>Critical</option></select><span class="muted">${products.length} products shown</span></div>
        <div class="table-wrap"><table><thead><tr><th>Product</th><th>Status</th><th>Quantity on hand</th><th>Reorder point</th><th>Safety stock</th><th>Inventory cost</th><th>Actions</th></tr></thead><tbody>
          ${products.map((p) => `<tr><td><div class="product-cell"><div class="product-thumb">${productEmoji(p.category)}</div><div><div class="product-name">${esc(p.name)}</div><div class="product-meta">${esc(p.category)} · ${esc(p.sku)}</div></div></div></td><td>${statusBadge(stockStatus(p))}</td><td class="number"><strong>${p.stock}</strong> units</td><td>${p.reorderPoint}</td><td>${p.safetyStock}</td><td>${money(p.stock * p.purchasePrice)}</td><td><div class="decision-actions"><button class="btn btn-secondary btn-small" data-action="adjust-product" data-id="${p.id}">Adjust</button><button class="btn btn-secondary btn-small" data-action="history" data-id="${p.id}">History</button></div></td></tr>`).join("")}
        </tbody></table></div>
      </section>`, "Inventory");
  }

  function salesView() {
    return shell(`
      <div class="page-intro"><div><h1>Import product-level sales</h1><p>Turn a POS export into inventory movements and demand history.</p></div><div class="actions"><button class="btn btn-secondary" data-action="download-sample">${icon("download")} Download format</button></div></div>
      <div class="workflow-stepper"><div class="step active"><div class="step-num">1</div><div><div class="step-title">Upload sales</div><div class="step-sub">CSV from POS</div></div></div><div class="step ${importPreview ? "active" : ""}"><div class="step-num">2</div><div><div class="step-title">Validate rows</div><div class="step-sub">Match barcodes</div></div></div><div class="step"><div class="step-num">3</div><div><div class="step-title">Update stock</div><div class="step-sub">Create transactions</div></div></div><div class="step"><div class="step-num">4</div><div><div class="step-title">Reorder</div><div class="step-sub">Generate suggestions</div></div></div></div>
      <section class="card"><div class="card-body">
        <div class="upload-zone" id="upload-zone"><input type="file" accept=".csv,text/csv" id="sales-file" /><div class="upload-icon">${icons.upload}</div><h3>Drop your sales CSV here</h3><p>Required columns: sold_at, barcode, quantity, unit_price</p><div class="actions" style="justify-content:center"><button class="btn btn-primary" data-action="choose-file">Choose CSV file</button><button class="btn btn-secondary" data-action="demo-import">Use demo import</button></div><div class="format-note">Unknown barcodes and invalid values are rejected before inventory is changed.</div></div>
        ${importPreview ? importPreviewHTML() : ""}
      </div></section>
      <section class="card" style="margin-top:18px"><div class="card-header"><div><h2>Latest import behavior</h2><p>What the production workflow does</p></div></div><div class="card-body"><div class="grid" style="grid-template-columns:repeat(3,1fr)"><div><strong>1. Validate</strong><p class="muted">Check required columns, dates, quantities, prices, and known barcodes.</p></div><div><strong>2. Prevent duplicates</strong><p class="muted">The backend hashes each sale and rejects duplicate rows or duplicate files.</p></div><div><strong>3. Update inventory</strong><p class="muted">FastAPI writes sales and auditable inventory transactions in one database operation.</p></div></div></div></section>`, "Sales import");
  }

  function importPreviewHTML() {
    return `<div style="margin-top:20px"><div class="card-header" style="padding-left:0;padding-right:0"><div><h3>Import preview</h3><p>${esc(importPreview.fileName)}</p></div></div><div class="import-summary"><div class="summary-tile"><strong>${importPreview.total}</strong><span>Rows received</span></div><div class="summary-tile"><strong>${importPreview.valid.length}</strong><span>Valid rows</span></div><div class="summary-tile"><strong>${importPreview.invalid.length}</strong><span>Rejected rows</span></div><div class="summary-tile"><strong>${importPreview.duplicates}</strong><span>Duplicates skipped</span></div></div>
      ${importPreview.invalid.length ? `<div class="callout callout-warning" style="margin-top:15px">${icons.alert}<div><strong>${importPreview.invalid.length} rows need attention</strong><p>${esc(importPreview.invalid.slice(0,3).map(x => `Row ${x.row}: ${x.reason}`).join(" · "))}</p></div></div>` : ""}
      <div class="actions" style="margin-top:15px"><button class="btn btn-primary" data-action="commit-import" ${!importPreview.valid.length ? "disabled" : ""}>Send file to backend</button><button class="btn btn-secondary" data-action="clear-import">Clear</button></div></div>`;
  }

  function recommendationsView() {
    const recs = state.recommendations;
    const pending = recs.filter((r) => r.status === "PENDING").length;
    const accepted = recs.filter((r) => ["ACCEPTED", "MODIFIED"].includes(r.status)).length;
    const estimated = recs.filter((r) => ["ACCEPTED", "MODIFIED", "PENDING"].includes(r.status)).reduce((sum, r) => {
      const p = productById(r.productId); return sum + (p ? r.recommendedCases * p.unitsPerCase * p.purchasePrice : 0);
    }, 0);

    return shell(`
      <div class="page-intro"><div><h1>Explainable reorder engine</h1><p>Review suggestions based on recent sales, stock, lead time, and case-pack size.</p></div><div class="actions"><button class="btn btn-secondary" data-action="generate-recommendations">${icon("refresh")} Recalculate</button>${accepted ? `<button class="btn btn-primary" data-action="create-orders">${icon("orders")} Create purchase orders</button>` : ""}</div></div>
      <div class="callout callout-info">${icons.info}<div><strong>Human approval stays in control</strong><p>The system recommends quantities and explains why. The store owner accepts, changes, or rejects each suggestion before an order is created.</p></div></div>
      <section class="card">
        ${recs.length ? `<div class="recommendation-summary"><div class="rec-stat"><span>Total suggestions</span><strong>${recs.length}</strong></div><div class="rec-stat"><span>Pending review</span><strong>${pending}</strong></div><div class="rec-stat"><span>Accepted</span><strong>${accepted}</strong></div><div class="rec-stat"><span>Estimated wholesale</span><strong>${money(estimated)}</strong></div></div><div class="table-wrap"><table><thead><tr><th>Product</th><th>Current</th><th>Avg/day</th><th>Suggested cases</th><th>Estimated cost</th><th>Why</th><th>Decision</th></tr></thead><tbody>
          ${recs.map((r) => { const p = productById(r.productId); if (!p) return ""; return `<tr><td><div class="product-cell"><div class="product-thumb">${productEmoji(p.category)}</div><div><div class="product-name">${esc(p.name)}</div><div class="product-meta">${esc(supplierById(p.supplierId)?.name || "")}</div></div></div></td><td>${r.currentStock}</td><td>${num(r.averageDailySales)}</td><td><input class="case-input" type="number" min="0" value="${r.recommendedCases}" data-rec-cases="${r.id}" /></td><td>${money(r.recommendedCases * p.unitsPerCase * p.purchasePrice)}</td><td><div class="reason">${esc(r.reason)}</div></td><td>${r.status === "PENDING" ? `<div class="decision-actions"><button class="btn btn-primary btn-small" data-action="accept-rec" data-id="${r.id}">Accept</button><button class="btn btn-secondary btn-small" data-action="reject-rec" data-id="${r.id}">Reject</button></div>` : statusBadge(r.status.toLowerCase(), r.status[0] + r.status.slice(1).toLowerCase())}</td></tr>`; }).join("")}
        </tbody></table></div>` : `<div class="empty"><div class="empty-icon">${icons.sparkles}</div><h3>No recommendations yet</h3><p>Run the reorder engine to analyze the latest 28 days of sales and identify products that may run out before the next delivery.</p><button class="btn btn-primary" data-action="generate-recommendations">Generate recommendations</button></div>`}
      </section>`, "Reorder engine");
  }

  function ordersView() {
    const orders = [...state.purchaseOrders].sort((a,b) => b.createdAt.localeCompare(a.createdAt));
    return shell(`
      <div class="page-intro"><div><h1>Purchase orders</h1><p>Supplier-specific orders created from approved recommendations.</p></div><div class="actions"><a class="btn btn-secondary" href="#recommendations">${icon("sparkles")} Review recommendations</a></div></div>
      ${orders.length ? `<div class="grid po-grid">${orders.map((po) => { const supplier = supplierById(po.supplierId); const total = po.items.reduce((sum, item) => sum + item.cases * item.unitsPerCase * item.unitCost, 0); return `<section class="card po-card"><div class="po-top"><div><div class="po-number">${esc(po.poNumber || po.id)}</div><div class="po-supplier">${esc(supplier?.name || "Unknown supplier")}</div></div>${statusBadge(po.status.toLowerCase(), po.status[0] + po.status.slice(1).toLowerCase())}</div><div class="po-details"><div class="po-detail"><span>ORDER VALUE</span><strong>${money(total)}</strong></div><div class="po-detail"><span>PRODUCTS</span><strong>${po.items.length}</strong></div><div class="po-detail"><span>CREATED</span><strong>${shortDate(po.createdAt.slice(0,10))}</strong></div><div class="po-detail"><span>DELIVERY</span><strong>${esc(supplier?.deliveryDays || "—")}</strong></div></div><div class="po-actions"><button class="btn btn-secondary btn-small" data-action="view-order" data-id="${po.id}">View</button>${po.status === "DRAFT" ? `<button class="btn btn-primary btn-small" data-action="approve-order" data-id="${po.id}">Approve</button>` : ""}${["APPROVED", "PARTIALLY_RECEIVED"].includes(po.status) ? `<button class="btn btn-primary btn-small" data-action="receive-order" data-id="${po.id}">Receive</button>` : ""}</div></section>`; }).join("")}</div>` : `<section class="card"><div class="empty"><div class="empty-icon">${icons.orders}</div><h3>No purchase orders yet</h3><p>Accept reorder recommendations, then group them into supplier-specific draft purchase orders.</p><a class="btn btn-primary" href="#recommendations">Open reorder engine</a></div></section>`}`, "Purchase orders");
  }

  function loginView() {
    return `<div class="login-screen"><div class="login-layout"><section class="login-brand-panel"><div class="brand login-brand"><div class="brand-mark large">${icons.logo}</div><div><div class="brand-name">StoreFlow</div><div class="brand-sub">Inventory intelligence</div></div></div><div class="login-message"><span class="eyebrow">FORWARD DEPLOYED ENGINEERING PROJECT</span><h1>Turn weekly shelf checks into explainable purchase orders.</h1><p>StoreFlow connects product-level sales, an auditable inventory ledger, human-approved reorder recommendations, and supplier receiving in one workflow.</p></div><div class="login-workflow"><span>Sales import</span><b>→</b><span>Inventory</span><b>→</b><span>Reorder</span><b>→</b><span>Purchase order</span></div></section><section class="login-card"><div><span class="eyebrow">SECURE DEMO</span><h2>Sign in to StoreFlow</h2><p>Use the seeded store-owner account to access the PostgreSQL-backed workflow.</p></div><form id="login-form" class="login-form"><div class="field"><label>Email address</label><input type="email" name="email" value="admin@storeflow.demo" autocomplete="username" required /></div><div class="field"><label>Password</label><input type="password" name="password" value="StoreFlow123!" autocomplete="current-password" minlength="8" required /></div><button class="btn btn-primary btn-block login-button" type="submit">Sign in</button><div id="login-error" class="login-error" hidden></div></form><div class="demo-credentials"><strong>Demo credentials</strong><code>admin@storeflow.demo</code><code>StoreFlow123!</code><p>The access token is stored only for this browser tab.</p></div><div class="api-note"><span class="connection-dot"></span> API expected at ${esc(API_BASE)}</div></section></div></div>`;
  }

  function render() {
    if (initialLoading) {
      app.innerHTML = `<div class="startup-screen"><div class="startup-card"><div class="brand-mark large">${icons.logo}</div><h1>Connecting to StoreFlow</h1><p>Checking your session and loading PostgreSQL data...</p><div class="loading-bar"><span></span></div></div></div>`;
      return;
    }
    if (!auth.token || !auth.user) {
      app.innerHTML = loginView();
      return;
    }
    if (apiError) {
      app.innerHTML = `<div class="startup-screen"><div class="startup-card error-card"><div class="error-icon">${icons.alert}</div><h1>Backend connection failed</h1><p>${esc(apiError)}</p><div class="endpoint-box">Expected API: ${esc(API_BASE)}</div><button class="btn btn-primary" data-action="retry-api">Try again</button></div></div>`;
      return;
    }
    const views = { dashboard: dashboardView, products: productsView, inventory: inventoryView, sales: salesView, recommendations: recommendationsView, orders: ordersView };
    app.innerHTML = (views[route()] || dashboardView)(); bindViewEvents(); window.scrollTo({ top: 0, behavior: "instant" });
  }

  function bindViewEvents() {
    document.getElementById("product-search")?.addEventListener("input", (event) => {
      productQuery = event.target.value;
      const cursor = event.target.selectionStart;
      app.innerHTML = productsView(); bindViewEvents();
      const input = document.getElementById("product-search"); input?.focus(); input?.setSelectionRange(cursor, cursor);
    });
    document.getElementById("category-filter")?.addEventListener("change", (event) => { categoryFilter = event.target.value; render(); });
    document.getElementById("inventory-filter")?.addEventListener("change", (event) => { inventoryFilter = event.target.value; render(); });
    document.querySelectorAll("[data-rec-cases]").forEach((input) => input.addEventListener("change", (event) => updateRecommendationCases(event.target.dataset.recCases, Number(event.target.value))));

    const fileInput = document.getElementById("sales-file");
    fileInput?.addEventListener("change", (event) => { if (event.target.files?.[0]) readSalesFile(event.target.files[0]); });
    const zone = document.getElementById("upload-zone");
    zone?.addEventListener("dragover", (event) => { event.preventDefault(); zone.classList.add("dragging"); });
    zone?.addEventListener("dragleave", () => zone.classList.remove("dragging"));
    zone?.addEventListener("drop", (event) => { event.preventDefault(); zone.classList.remove("dragging"); if (event.dataTransfer.files?.[0]) readSalesFile(event.dataTransfer.files[0]); });
  }

  app.addEventListener("submit", async (event) => {
    if (event.target.id !== "login-form") return;
    event.preventDefault();
    const form = event.target;
    if (!form.reportValidity()) return;
    const button = form.querySelector("button[type='submit']");
    const errorBox = document.getElementById("login-error");
    const values = Object.fromEntries(new FormData(form).entries());
    button.disabled = true;
    button.textContent = "Signing in…";
    errorBox.hidden = true;
    try {
      await signIn(String(values.email).trim(), String(values.password));
    } catch (error) {
      errorBox.textContent = error.message;
      errorBox.hidden = false;
      button.disabled = false;
      button.textContent = "Sign in";
    }
  });

  app.addEventListener("click", (event) => {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    const id = target.dataset.id;
    const handlers = {
      "refresh-data": () => resetState(),
      "reset-demo": resetDemoData,
      "logout": signOut,
      "retry-api": () => refreshData({ showLoader: true }),
      "toggle-menu": () => document.getElementById("sidebar")?.classList.toggle("open"),
      "add-product": () => productModal(),
      "edit-product": () => productModal(productById(id)),
      "record-adjustment": () => inventoryModal("adjustment"),
      "adjust-product": () => inventoryModal("adjustment", productById(id)),
      "receive-stock": () => inventoryModal("receive"),
      "history": () => historyModal(productById(id)),
      "choose-file": () => document.getElementById("sales-file")?.click(),
      "download-sample": downloadSampleSales,
      "demo-import": demoImport,
      "commit-import": commitImport,
      "clear-import": () => { importPreview = null; pendingImportFile = null; render(); },
      "generate-recommendations": generateRecommendations,
      "accept-rec": () => setRecommendationStatus(id, "ACCEPTED"),
      "reject-rec": () => setRecommendationStatus(id, "REJECTED"),
      "create-orders": createPurchaseOrders,
      "view-order": () => orderModal(id),
      "approve-order": () => approveOrder(id),
      "receive-order": () => receiveOrder(id),
      "download-order": () => downloadOrder(id),
    };
    handlers[action]?.();
  });

  document.addEventListener("click", (event) => {
    if (event.target.closest("[data-close-sidebar]")) document.getElementById("sidebar")?.classList.remove("open");
    if (event.target.matches(".modal-backdrop") || event.target.closest("[data-close-modal]")) closeModal();
  });

  window.addEventListener("hashchange", render);

  function toast(title, message) {
    toastRoot.innerHTML = `<div class="toast"><strong>${esc(title)}</strong><span>${esc(message)}</span></div>`;
    clearTimeout(window.__storeflowToast);
    window.__storeflowToast = setTimeout(() => { toastRoot.innerHTML = ""; }, 3400);
  }

  function showModal({ title, subtitle = "", body, footer = "", wide = false }) {
    modalRoot.innerHTML = `<div class="modal-backdrop"><div class="modal ${wide ? "wide" : ""}"><div class="modal-header"><div><h2>${esc(title)}</h2>${subtitle ? `<p>${esc(subtitle)}</p>` : ""}</div><button class="modal-close" data-close-modal aria-label="Close">×</button></div><div class="modal-body">${body}</div>${footer ? `<div class="modal-footer">${footer}</div>` : ""}</div></div>`;
  }
  function closeModal() { modalRoot.innerHTML = ""; }

  function productModal(product = null) {
    const isEdit = Boolean(product);
    showModal({
      title: isEdit ? "Edit product" : "Add product",
      subtitle: isEdit ? "SKU and barcode remain fixed after creation to protect sales history." : "Configure identification, supplier, and reorder settings.",
      body: `<form id="product-form" class="form-grid">
        <div class="field full"><label>Product name</label><input required name="name" value="${esc(product?.name || "")}" placeholder="Example: Coca-Cola 20 oz" /></div>
        <div class="field"><label>SKU</label><input required name="sku" ${isEdit ? "disabled" : ""} value="${esc(product?.sku || "")}" placeholder="SF-BEV-049" /></div>
        <div class="field"><label>Barcode</label><input required name="barcode" ${isEdit ? "disabled" : ""} value="${esc(product?.barcode || "")}" placeholder="12-digit barcode" /></div>
        <div class="field"><label>Category</label><select name="category">${["Beverages","Chips","Candy","Household"].map(c => `<option ${product?.category === c ? "selected" : ""}>${c}</option>`).join("")}</select></div>
        <div class="field"><label>Supplier</label><select name="supplierId">${state.suppliers.map(s => `<option value="${s.id}" ${product?.supplierId === s.id ? "selected" : ""}>${esc(s.name)}</option>`).join("")}</select></div>
        <div class="field"><label>Purchase price</label><input required min="0.01" step="0.01" type="number" name="purchasePrice" value="${product?.purchasePrice ?? ""}" /></div>
        <div class="field"><label>Selling price</label><input required min="0.01" step="0.01" type="number" name="sellingPrice" value="${product?.sellingPrice ?? ""}" /></div>
        <div class="field"><label>Units per case</label><input required min="1" type="number" name="unitsPerCase" value="${product?.unitsPerCase ?? 12}" /></div>
        <div class="field"><label>${isEdit ? "Current stock (read only)" : "Opening stock"}</label><input required min="0" type="number" name="stock" ${isEdit ? "disabled" : ""} value="${product?.stock ?? 0}" /></div>
        <div class="field"><label>Reorder point</label><input required min="0" type="number" name="reorderPoint" value="${product?.reorderPoint ?? 10}" /></div>
        <div class="field"><label>Safety stock</label><input required min="0" type="number" name="safetyStock" value="${product?.safetyStock ?? 4}" /></div>
        <div class="field"><label>Lead time (days)</label><input required min="0" type="number" name="leadTimeDays" value="${product?.leadTimeDays ?? 4}" /></div>
      </form>`,
      footer: `<button class="btn btn-secondary" data-close-modal>Cancel</button><button class="btn btn-primary" id="save-product">${isEdit ? "Save changes" : "Add product"}</button>`
    });
    document.getElementById("save-product").addEventListener("click", async () => {
      const form = document.getElementById("product-form");
      if (!form.reportValidity()) return;
      const values = Object.fromEntries(new FormData(form).entries());
      const common = {
        name: values.name, category: values.category, supplier_id: values.supplierId,
        purchase_price: Number(values.purchasePrice), selling_price: Number(values.sellingPrice),
        units_per_case: Number(values.unitsPerCase), reorder_point: Number(values.reorderPoint),
        safety_stock: Number(values.safetyStock), lead_time_days: Number(values.leadTimeDays), is_active: true,
      };
      try {
        if (isEdit) {
          await apiFetch(`/products/${product.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(common) });
        } else {
          const numericIds = state.products.map((item) => Number(String(item.id).match(/(\d+)$/)?.[1] || 0));
          const nextId = `PRD-${String(Math.max(0, ...numericIds) + 1).padStart(3, "0")}`;
          await apiFetch("/products", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ id: nextId, sku: values.sku, barcode: values.barcode, opening_stock: Number(values.stock), ...common }) });
        }
        closeModal(); await refreshData(); toast(isEdit ? "Product updated" : "Product added", values.name);
      } catch (error) { toast("Product could not be saved", error.message); }
    });
  }
  function inventoryModal(mode, selectedProduct = null) {
    const isReceive = mode === "receive";
    showModal({
      title: isReceive ? "Receive inventory" : "Record inventory adjustment",
      subtitle: isReceive ? "Add delivered units to quantity on hand." : "Record damage, expiration, return, theft, or count correction.",
      body: `<form id="inventory-form" class="form-grid"><div class="field full"><label>Product</label><select name="productId">${state.products.map(p => `<option value="${p.id}" ${selectedProduct?.id === p.id ? "selected" : ""}>${esc(p.name)} — ${p.stock} units</option>`).join("")}</select></div>
        <div class="field"><label>${isReceive ? "Cases received" : "Adjustment type"}</label>${isReceive ? `<input type="number" name="cases" value="1" min="0" required />` : `<select name="type"><option value="DAMAGE">Damage</option><option value="EXPIRATION">Expiration</option><option value="RETURN">Return</option><option value="THEFT">Theft / missing</option><option value="MANUAL_ADJUSTMENT">Manual correction</option></select>`}</div>
        <div class="field"><label>${isReceive ? "Extra individual units" : "Quantity change"}</label><input type="number" name="quantity" value="${isReceive ? 0 : -1}" ${isReceive ? "min=\"0\"" : ""} required /><div class="help">${isReceive ? "Full cases are converted using the product case-pack size." : "Use a negative number to remove stock and a positive number to add stock."}</div></div>
        <div class="field full"><label>Notes</label><textarea name="notes" placeholder="Example: Damaged during unloading or physical count correction"></textarea></div></form>`,
      footer: `<button class="btn btn-secondary" data-close-modal>Cancel</button><button class="btn btn-primary" id="save-inventory">${isReceive ? "Receive stock" : "Save adjustment"}</button>`
    });
    document.getElementById("save-inventory").addEventListener("click", async () => {
      const form = document.getElementById("inventory-form"); if (!form.reportValidity()) return;
      const values = Object.fromEntries(new FormData(form).entries());
      const product = productById(values.productId); if (!product) return;
      const change = isReceive ? Number(values.cases) * product.unitsPerCase + Number(values.quantity || 0) : Number(values.quantity);
      if (!Number.isInteger(change) || change === 0) return toast("Nothing changed", "Enter a non-zero whole-unit quantity.");
      if (product.stock + change < 0) return toast("Cannot reduce below zero", `${product.name} currently has ${product.stock} units.`);
      try {
        if (isReceive) await apiFetch("/inventory/receive", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ product_id: product.id, quantity: change, notes: values.notes || null }) });
        else await apiFetch("/inventory/adjust", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ product_id: product.id, transaction_type: values.type, quantity_change: change, notes: values.notes || null }) });
        closeModal(); await refreshData(); toast("Inventory updated", `${product.name}: ${change > 0 ? "+" : ""}${change} units`);
      } catch (error) { toast("Inventory update failed", error.message); }
    });
  }
  async function historyModal(product) {
    showModal({ title: `${product.name} history`, subtitle: "Loading inventory transactions...", body: `<div class="modal-loading">Loading...</div>` });
    try {
      const transactions = await apiFetch(`/inventory/${product.id}/history`);
      showModal({ title: `${product.name} history`, subtitle: `Current quantity: ${product.stock} units`, wide: true,
        body: transactions.length ? `<div class="table-wrap"><table><thead><tr><th>Date</th><th>Type</th><th>Change</th><th>Reference</th><th>Notes</th></tr></thead><tbody>${transactions.map(t => `<tr><td>${dateTime(t.created_at)}</td><td>${esc(t.transaction_type.replaceAll("_", " "))}</td><td><strong style="color:${t.quantity_change >= 0 ? "var(--green)" : "var(--red)"}">${t.quantity_change > 0 ? "+" : ""}${t.quantity_change}</strong></td><td class="muted">${esc(t.reference_type || "—")}</td><td class="muted">${esc(t.notes || "—")}</td></tr>`).join("")}</tbody></table></div>` : `<div class="empty"><h3>No transactions recorded</h3><p>This product does not yet have inventory ledger entries.</p></div>` });
    } catch (error) { closeModal(); toast("History could not be loaded", error.message); }
  }
  function parseCSV(text) {
    const rows = [];
    let row = [], cell = "", quoted = false;
    for (let i = 0; i < text.length; i++) {
      const char = text[i], next = text[i + 1];
      if (char === '"' && quoted && next === '"') { cell += '"'; i++; }
      else if (char === '"') quoted = !quoted;
      else if (char === ',' && !quoted) { row.push(cell.trim()); cell = ""; }
      else if ((char === '\n' || char === '\r') && !quoted) {
        if (char === '\r' && next === '\n') i++;
        row.push(cell.trim()); cell = "";
        if (row.some(Boolean)) rows.push(row); row = [];
      } else cell += char;
    }
    row.push(cell.trim()); if (row.some(Boolean)) rows.push(row);
    if (!rows.length) return [];
    const headers = rows.shift().map(h => h.trim().toLowerCase());
    return rows.map((values) => Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""])));
  }

  function validateSalesRows(rows, fileName) {
    const required = ["sold_at", "barcode", "quantity", "unit_price"];
    if (!rows.length || !required.every(key => Object.prototype.hasOwnProperty.call(rows[0] || {}, key))) {
      importPreview = { fileName, total: rows.length, valid: [], invalid: [{ row: 1, reason: `Missing required columns: ${required.join(", ")}` }], duplicates: 0 };
      return;
    }
    const existingKeys = new Set(state.salesDaily.map(s => `${s.date}|${s.barcode}|${s.quantity}|${s.revenue}`));
    const valid = [], invalid = []; let duplicates = 0;
    rows.forEach((row, index) => {
      const product = productByBarcode(row.barcode);
      const quantity = Number(row.quantity); const price = Number(row.unit_price);
      const parsedDate = new Date(row.sold_at);
      if (!product) invalid.push({ row: index + 2, reason: `Unknown barcode ${row.barcode}` });
      else if (!Number.isInteger(quantity) || quantity <= 0) invalid.push({ row: index + 2, reason: "Quantity must be a positive whole number" });
      else if (!Number.isFinite(price) || price < 0) invalid.push({ row: index + 2, reason: "Unit price is invalid" });
      else if (Number.isNaN(parsedDate.getTime())) invalid.push({ row: index + 2, reason: "sold_at is not a valid date" });
      else {
        const normalized = { date: parsedDate.toISOString().slice(0,10), barcode: row.barcode, quantity, revenue: Number((quantity * price).toFixed(2)), productId: product.id };
        const key = `${normalized.date}|${normalized.barcode}|${normalized.quantity}|${normalized.revenue}`;
        if (existingKeys.has(key)) duplicates++; else { valid.push(normalized); existingKeys.add(key); }
      }
    });
    importPreview = { fileName, total: rows.length, valid, invalid, duplicates };
  }

  function readSalesFile(file) {
    if (!file.name.toLowerCase().endsWith(".csv")) return toast("Unsupported file", "Please upload a CSV file.");
    const reader = new FileReader();
    reader.onload = () => { pendingImportFile = file; validateSalesRows(parseCSV(String(reader.result)), file.name); render(); };
    reader.onerror = () => toast("Could not read file", "Try saving the CSV again.");
    reader.readAsText(file);
  }
  function demoImport() {
    const selected = state.products.slice(0,8).map((p,i) => ({ sold_at: `${todayISO()}T${String(10+i).padStart(2,"0")}:15:00Z`, barcode: p.barcode, quantity: String(1+(i%3)), unit_price: String(p.sellingPrice) }));
    selected.push({ sold_at: `${todayISO()}T18:00:00Z`, barcode: "000000000000", quantity: "2", unit_price: "1.99" });
    const csv = ["sold_at,barcode,quantity,unit_price", ...selected.map((row) => `${row.sold_at},${row.barcode},${row.quantity},${row.unit_price}`)].join("\n");
    pendingImportFile = new File([csv], `demo_sales_import_${Date.now()}.csv`, { type: "text/csv" });
    validateSalesRows(selected, pendingImportFile.name); render();
  }
  async function commitImport() {
    if (!pendingImportFile) return toast("No file selected", "Choose or generate a CSV first.");
    const formData = new FormData(); formData.append("file", pendingImportFile);
    try {
      const result = await apiFetch("/sales/import", { method: "POST", body: formData });
      importPreview = null; pendingImportFile = null; await refreshData();
      toast("Sales import complete", `${result.rows_imported} imported, ${result.rows_rejected} rejected, ${result.duplicates_skipped} duplicates skipped.`);
    } catch (error) { toast("Sales import failed", error.message); }
  }
  function downloadBlob(filename, content, type = "text/csv") {
    const blob = new Blob([content], { type }); const url = URL.createObjectURL(blob);
    const link = document.createElement("a"); link.href = url; link.download = filename; document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
  }

  function downloadSampleSales() {
    const sample = ["sold_at,barcode,quantity,unit_price", ...state.products.slice(0,5).map((p,i) => `${todayISO()}T${10+i}:00:00,${p.barcode},${1+i%2},${p.sellingPrice.toFixed(2)}`)].join("\n");
    downloadBlob("storeflow-sales-import-template.csv", sample); toast("Template downloaded", "Use the exact column names shown in the file.");
  }

  async function generateRecommendations() {
    try {
      const result = await apiFetch("/recommendations/generate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ history_days: 28, review_cycle_days: 7 }) });
      await refreshData(); toast("Recommendations ready", `${result.generated_count} products need review.`);
    } catch (error) { toast("Recommendations failed", error.message); }
  }
  async function updateRecommendationCases(id, cases) {
    const recommendation = state.recommendations.find((item) => item.id === id); if (!recommendation) return;
    const decidedCases = Math.max(0, Math.floor(cases || 0));
    try {
      await apiFetch(`/recommendations/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ status: "MODIFIED", decided_cases: decidedCases }) });
      await refreshData(); toast("Quantity updated", `${decidedCases} cases will be used if ordered.`);
    } catch (error) { toast("Quantity could not be updated", error.message); }
  }
  async function setRecommendationStatus(id, status) {
    const recommendation = state.recommendations.find((item) => item.id === id); if (!recommendation) return;
    const wasModified = recommendation.recommendedCases !== recommendation.originalCases;
    const payload = status === "ACCEPTED" && wasModified ? { status: "MODIFIED", decided_cases: recommendation.recommendedCases } : { status };
    try { await apiFetch(`/recommendations/${id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) }); await refreshData(); }
    catch (error) { toast("Decision could not be saved", error.message); }
  }
  async function createPurchaseOrders() {
    try {
      const result = await apiFetch("/purchase-orders/from-recommendations", { method: "POST" });
      await refreshData(); location.hash = "orders"; toast("Purchase orders created", `${result.created_count} supplier drafts are ready for approval.`);
    } catch (error) { toast("Orders could not be created", error.message); }
  }
  async function approveOrder(id) {
    try { const order = await apiFetch(`/purchase-orders/${id}/approve`, { method: "POST" }); closeModal(); await refreshData(); toast("Order approved", `${order.po_number} is ready for the supplier.`); }
    catch (error) { toast("Order could not be approved", error.message); }
  }
  async function receiveOrder(id) {
    try {
      const order = await apiFetch(`/purchase-orders/${id}/receive`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ items: null }) });
      closeModal(); await refreshData(); toast("Delivery received", `${order.po_number} updated inventory in PostgreSQL.`);
    } catch (error) { toast("Delivery could not be received", error.message); }
  }
  function orderModal(id) {
    const po = state.purchaseOrders.find((order) => order.id === id); if (!po) return;
    const supplier = supplierById(po.supplierId);
    const total = po.estimatedTotal || po.items.reduce((sum,item) => sum + item.lineTotal, 0);
    showModal({ title: po.poNumber || po.id, subtitle: supplier?.name || po.supplierName || "Supplier order", wide: true,
      body: `<div class="callout callout-info">${icons.info}<div><strong>${esc(supplier?.deliveryDays || "Delivery schedule unavailable")}</strong><p>${esc(supplier?.email || "")} · Minimum order ${money(supplier?.minimumOrder || 0)}</p></div></div><div>${po.items.map((item) => `<div class="po-line"><div><div class="product-name">${esc(item.productName || productById(item.productId)?.name || "Unknown product")}</div><div class="product-meta">${esc(item.sku || productById(item.productId)?.sku || "")}</div></div><div><strong>${item.cases}</strong> cases</div><div>${money(item.lineTotal || item.cases * item.unitsPerCase * item.unitCost)}</div></div>`).join("")}</div><div class="po-total"><span>Total</span><span>${money(total)}</span></div>`,
      footer: `<button class="btn btn-secondary" data-action="download-order" data-id="${po.id}">${icon("download")} Export CSV</button>${po.status === "DRAFT" ? `<button class="btn btn-primary" data-action="approve-order" data-id="${po.id}">Approve order</button>` : ""}${["APPROVED","PARTIALLY_RECEIVED"].includes(po.status) ? `<button class="btn btn-primary" data-action="receive-order" data-id="${po.id}">Receive remaining delivery</button>` : ""}` });
  }
  async function downloadOrder(id) {
    const po = state.purchaseOrders.find((order) => order.id === id); if (!po) return;
    try {
      const response = await fetch(`${API_BASE}/purchase-orders/${id}/export`, { headers: { Authorization: `Bearer ${auth.token}` } });
      if (!response.ok) throw new Error(`Export failed with status ${response.status}`);
      const blob = await response.blob(); const url = URL.createObjectURL(blob);
      const link = document.createElement("a"); link.href = url; link.download = `${po.poNumber || po.id}.csv`;
      document.body.appendChild(link); link.click(); link.remove(); URL.revokeObjectURL(url);
      toast("Purchase order exported", `${po.poNumber || po.id}.csv was downloaded.`);
    } catch (error) { toast("Export failed", error.message); }
  }

  bootstrap();
})();
