const archivo = document.getElementById('archivo');
const texto = document.getElementById('contenido');
const nombre = document.getElementById('nombre-archivo');
const base = nombre.textContent;

archivo.addEventListener('change', async () => {
  const f = archivo.files[0];
  if (!f) return;
  texto.value = await f.text();
  nombre.textContent = f.name;
});
texto.addEventListener('input', () => { archivo.value = ''; nombre.textContent = base; });

document.querySelectorAll('.pastillas').forEach(grupo => {
  const botones = grupo.querySelectorAll('button');
  const paneles = document.querySelectorAll('.panel-token');
  botones.forEach(b => b.addEventListener('click', () => {
    botones.forEach(x => x.setAttribute('aria-selected', x === b));
    paneles.forEach(p => p.hidden = p.id !== 'panel-' + b.dataset.token);
  }));
});
