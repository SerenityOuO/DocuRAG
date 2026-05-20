<template>
  <section>
    <header class="page-header">
      <div>
        <h2 class="page-title">Documents</h2>
        <p class="page-description">
          Invoice Demo 的文件處理狀態。
        </p>
      </div>
    </header>

    <div class="panel">
      <table class="table">
        <thead>
          <tr>
            <th>Filename</th>
            <th>Type</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>invoice_001.pdf</td>
            <td>invoice</td>
            <td><span class="status status-indexed">indexed</span></td>
          </tr>
          <tr>
            <td>contract_001.pdf</td>
            <td>contract</td>
            <td><span class="status status-uploaded">uploaded</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
