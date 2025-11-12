function displayTable(data, type) {
  const content = document.getElementById("content");
  content.innerHTML = `<h2>${type}</h2>`;

  if (!data || data.length === 0) {
    content.innerHTML += `<p>No ${type.toLowerCase()} found.</p>`;
    return;
  }

  let table = `<table><thead><tr>`;
  Object.keys(data[0]).forEach(key => {
    table += `<th>${key}</th>`;
  });
  table += `</tr></thead><tbody>`;

  data.forEach(item => {
    table += `<tr>`;
    Object.values(item).forEach(value => {
      table += `<td>${value}</td>`;
    });
    table += `</tr>`;
  });

  table += `</tbody></table>`;
  content.innerHTML += table;
}
