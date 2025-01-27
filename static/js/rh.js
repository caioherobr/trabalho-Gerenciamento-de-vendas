// Elementos dos botões
const menuToggleCadastro = document.getElementById('menu-toggle-cadastro');
const submenuCadastro = document.getElementById('submenu-cadastro');

const openaddgerenteBtn = document.getElementById('openaddgerenteBtn');
const openaddvendedorBtn = document.getElementById('openaddvendedorBtn');
const openAlterarSenhaBtn = document.getElementById('openAlterarSenhaBtn');
const openVisualizarSenhaBtn = document.getElementById('openVisualizarSenhaBtn');
const openExcluirUsuarioBtn = document.getElementById('openExcluirUsuarioBtn');

// Elementos das seções
const addgerenteDiv = document.getElementById('addgerenteDiv');
const addvendedorDiv = document.getElementById('addvendedorDiv');
const alterarSenhaDiv = document.getElementById('alterarSenhaDiv');
const visualizarSenhaDiv = document.getElementById('visualizarSenhaDiv');
const excluirUsuarioDiv = document.getElementById('excluirUsuarioDiv');

// Lista de todas as seções
const sections = [addgerenteDiv, addvendedorDiv, alterarSenhaDiv, visualizarSenhaDiv, excluirUsuarioDiv];

// Função para alternar visibilidade
function toggleVisibility(targetDiv) {
    // Oculta todas as seções
    sections.forEach(div => div.classList.add('hidden'));
    // Exibe apenas a seção selecionada
    targetDiv.classList.remove('hidden');
}

// Evento do menu para exibir/ocultar o submenu
menuToggleCadastro.addEventListener('click', () => {
    submenuCadastro.classList.toggle('hidden');
});

// Eventos dos botões para alternar as seções
openaddgerenteBtn.addEventListener('click', () => toggleVisibility(addgerenteDiv));
openaddvendedorBtn.addEventListener('click', () => toggleVisibility(addvendedorDiv));
openAlterarSenhaBtn.addEventListener('click', () => toggleVisibility(alterarSenhaDiv));
openVisualizarSenhaBtn.addEventListener('click', () => toggleVisibility(visualizarSenhaDiv));
openExcluirUsuarioBtn.addEventListener('click', () => toggleVisibility(excluirUsuarioDiv));
 
 // Função para mostrar o Popup Cadastro Gerente
    function showPopup(message) {
        alert(message); // Pode ser substituído por qualquer outro tipo de popup, como SweetAlert.
    }

    document.getElementById('addGerenteForm').addEventListener('submit', function(event) {
        event.preventDefault();

        showPopup('Gerente cadastrado com sucesso!');

});
 // Função para mostrar o Popup Cadastro Vendedor
    function showPopup(message) {
        alert(message);
    }
        document.getElementById('addVendedorForm').addEventListener('submit', function(event) {
            event.preventDefault();
            showPopup('Vendedor cadastrado com sucesso!');


});