export function exportRowsToExcel(fileName, rows) {
  if (!rows || !rows.length) {
    return;
  }

  let table = '<table><tr>';
  rows[0].forEach((cell) => {
    table += '<th style="background:#f8f8f9;font-weight:bold;border:1px solid #dcdfe6;">' + escapeHtml(cell) + '</th>';
  });
  table += '</tr>';

  for (let i = 1; i < rows.length; i++) {
    table += '<tr>';
    rows[i].forEach((cell) => {
      const value = cell === null || cell === undefined ? '' : cell;
      table += '<td style="border:1px solid #dcdfe6;">' + escapeHtml(value) + '</td>';
    });
    table += '</tr>';
  }

  table += '</table>';

  const excelContent = '<html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40"><head><meta charset="UTF-8"></head><body>' + table + '</body></html>';
  const blob = new Blob(['\ufeff' + excelContent], {
    type: 'application/vnd.ms-excel;charset=utf-8;'
  });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);

  link.href = url;
  link.download = fileName + '.xls';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}






