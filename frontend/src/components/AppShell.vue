<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <h1 class="brand-title">DocuRAG</h1>
        <p class="brand-subtitle">AgentOps Demo Platform</p>
      </div>

      <nav class="nav-list" aria-label="Primary navigation">
        <RouterLink class="nav-link" to="/">Dashboard</RouterLink>
        <RouterLink class="nav-link" to="/login">Login</RouterLink>
        <RouterLink class="nav-link" to="/projects">Projects</RouterLink>
        <RouterLink class="nav-link" to="/documents">Documents</RouterLink>
      </nav>
    </aside>

    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
