/**
 * JavaScript Principal - HGU Digital Core
 * Funções auxiliares e utilitárias para todo o sistema
 */

// ============================================================================
// FUNÇÕES DE API
// ============================================================================

/**
 * Faz uma requisição POST para a API
 * @param {string} url - URL da API
 * @param {object} dados - Dados a serem enviados
 * @returns {Promise} - Promessa com a resposta
 */
async function fazerRequisicaoAPI(url, dados) {
    try {
        const resposta = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dados)
        });
        
        return await resposta.json();
    } catch (erro) {
        console.error('Erro na requisição:', erro);
        throw erro;
    }
}

/**
 * Faz uma requisição GET para a API
 * @param {string} url - URL da API
 * @returns {Promise} - Promessa com a resposta
 */
async function obterDadosAPI(url) {
    try {
        const resposta = await fetch(url);
        return await resposta.json();
    } catch (erro) {
        console.error('Erro ao obter dados:', erro);
        throw erro;
    }
}

// ============================================================================
// FUNÇÕES DE INTERFACE
// ============================================================================

/**
 * Mostra uma mensagem de alerta na tela
 * @param {string} mensagem - Texto da mensagem
 * @param {string} tipo - Tipo do alerta (sucesso, erro, aviso, info)
 */
function mostrarAlerta(mensagem, tipo = 'info') {
    const alertaDiv = document.createElement('div');
    alertaDiv.className = `alerta alerta-${tipo}`;
    alertaDiv.textContent = mensagem;
    
    // Inserir no início do container
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertaDiv, container.firstChild);
        
        // Remover após 5 segundos
        setTimeout(() => {
            alertaDiv.remove();
        }, 5000);
    }
}

/**
 * Mostra o indicador de loading
 */
function mostrarLoading() {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.classList.add('ativo');
    }
}

/**
 * Esconde o indicador de loading
 */
function esconderLoading() {
    const loading = document.querySelector('.loading');
    if (loading) {
        loading.classList.remove('ativo');
    }
}

/**
 * Abre um modal
 * @param {string} idModal - ID do modal a ser aberto
 */
function abrirModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.add('ativo');
    }
}

/**
 * Fecha um modal
 * @param {string} idModal - ID do modal a ser fechado
 */
function fecharModal(idModal) {
    const modal = document.getElementById(idModal);
    if (modal) {
        modal.classList.remove('ativo');
    }
}

// ============================================================================
// FUNÇÕES DE VALIDAÇÃO
// ============================================================================

/**
 * Valida se um campo está preenchido
 * @param {string} valor - Valor do campo
 * @returns {boolean} - True se válido
 */
function validarCampoObrigatorio(valor) {
    return valor && valor.trim() !== '';
}

/**
 * Valida formato de PREC-CP
 * @param {string} prec - PREC-CP a ser validado
 * @returns {boolean} - True se válido
 */
function validarPREC(prec) {
    // Formato básico: números e traço
    const regex = /^\d{3,}-\d{2,}$/;
    return regex.test(prec);
}

/**
 * Valida todos os campos obrigatórios de um formulário
 * @param {HTMLFormElement} formulario - Formulário a ser validado
 * @returns {boolean} - True se todos os campos obrigatórios estão preenchidos
 */
function validarFormulario(formulario) {
    const camposObrigatorios = formulario.querySelectorAll('[required]');
    let valido = true;
    
    camposObrigatorios.forEach(campo => {
        if (!validarCampoObrigatorio(campo.value)) {
            campo.style.borderColor = 'red';
            valido = false;
        } else {
            campo.style.borderColor = '';
        }
    });
    
    return valido;
}

// ============================================================================
// FUNÇÕES DE FORMATAÇÃO
// ============================================================================

/**
 * Formata data no padrão brasileiro
 * @param {string} dataISO - Data no formato ISO
 * @returns {string} - Data formatada (DD/MM/YYYY)
 */
function formatarData(dataISO) {
    if (!dataISO) return '';
    
    const data = new Date(dataISO);
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    
    return `${dia}/${mes}/${ano}`;
}

/**
 * Formata data e hora no padrão brasileiro
 * @param {string} dataISO - Data no formato ISO
 * @returns {string} - Data e hora formatadas (DD/MM/YYYY HH:MM)
 */
function formatarDataHora(dataISO) {
    if (!dataISO) return '';
    
    const data = new Date(dataISO);
    const dia = String(data.getDate()).padStart(2, '0');
    const mes = String(data.getMonth() + 1).padStart(2, '0');
    const ano = data.getFullYear();
    const hora = String(data.getHours()).padStart(2, '0');
    const minuto = String(data.getMinutes()).padStart(2, '0');
    
    return `${dia}/${mes}/${ano} ${hora}:${minuto}`;
}

// ============================================================================
// FUNÇÕES DE TABELA
// ============================================================================

/**
 * Preenche uma tabela com dados
 * @param {string} idTabela - ID da tabela
 * @param {Array} dados - Array de objetos com os dados
 * @param {Array} colunas - Array com nomes das colunas
 */
function preencherTabela(idTabela, dados, colunas) {
    const tbody = document.querySelector(`#${idTabela} tbody`);
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (dados.length === 0) {
        const tr = document.createElement('tr');
        const td = document.createElement('td');
        td.colSpan = colunas.length;
        td.textContent = 'Nenhum registro encontrado';
        td.style.textAlign = 'center';
        tr.appendChild(td);
        tbody.appendChild(tr);
        return;
    }
    
    dados.forEach(item => {
        const tr = document.createElement('tr');
        
        colunas.forEach(coluna => {
            const td = document.createElement('td');
            
            // Verificar se é uma coluna de data
            if (coluna.includes('data') && item[coluna]) {
                td.textContent = formatarDataHora(item[coluna]);
            } else {
                td.textContent = item[coluna] || '-';
            }
            
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}

// ============================================================================
// FUNÇÕES DE EXPORTAÇÃO
// ============================================================================

/**
 * Exporta tabela para CSV
 * @param {string} idTabela - ID da tabela
 * @param {string} nomeArquivo - Nome do arquivo CSV
 */
function exportarTabelaCSV(idTabela, nomeArquivo = 'dados.csv') {
    const tabela = document.getElementById(idTabela);
    if (!tabela) return;
    
    let csv = [];
    const linhas = tabela.querySelectorAll('tr');
    
    linhas.forEach(linha => {
        const colunas = linha.querySelectorAll('td, th');
        const dados = Array.from(colunas).map(col => col.textContent);
        csv.push(dados.join(','));
    });
    
    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = nomeArquivo;
    a.click();
    
    window.URL.revokeObjectURL(url);
}

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Fechar modais ao clicar fora
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('ativo');
            }
        });
    });
    
    // Marcar link ativo na navegação
    const paginaAtual = window.location.pathname;
    document.querySelectorAll('.navegacao a').forEach(link => {
        if (link.getAttribute('href') === paginaAtual) {
            link.classList.add('ativo');
        }
    });
});

// ============================================================================
// FUNÇÕES ESPECÍFICAS DE MÓDULOS
// ============================================================================

/**
 * Busca paciente por PREC-CP
 * @param {string} prec - PREC-CP do paciente
 * @returns {Promise} - Dados do paciente
 */
async function buscarPaciente(prec) {
    if (!validarPREC(prec)) {
        throw new Error('PREC-CP inválido');
    }
    
    const resposta = await obterDadosAPI(`/api/pacientes/buscar/${prec}`);
    return resposta;
}

/**
 * Lista todos os setores
 * @returns {Promise} - Lista de setores
 */
async function listarSetores() {
    const resposta = await obterDadosAPI('/api/setores/listar');
    return resposta.setores || [];
}

/**
 * Lista todos os profissionais
 * @returns {Promise} - Lista de profissionais
 */
async function listarProfissionais() {
    const resposta = await obterDadosAPI('/api/profissionais/listar');
    return resposta.profissionais || [];
}

/**
 * Preenche um select com opções
 * @param {string} idSelect - ID do select
 * @param {Array} opcoes - Array de objetos com id e nome
 * @param {string} campoId - Nome do campo ID
 * @param {string} campoNome - Nome do campo de exibição
 */
function preencherSelect(idSelect, opcoes, campoId = 'id', campoNome = 'nome') {
    const select = document.getElementById(idSelect);
    if (!select) return;
    
    // Limpar opções existentes (exceto a primeira)
    while (select.options.length > 1) {
        select.remove(1);
    }
    
    // Adicionar novas opções
    opcoes.forEach(opcao => {
        const option = document.createElement('option');
        option.value = opcao[campoId];
        option.textContent = opcao[campoNome];
        select.appendChild(option);
    });
}

