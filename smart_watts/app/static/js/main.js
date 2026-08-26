/* =============================================== */
/* app/static/js/main.js */
/* =============================================== */
/* Script principal de Smart Watts */
/* Contiene funcionalidades interactivas comunes */
/* =============================================== */

'use strict';

/**
 * Objeto global de Smart Watts
 * Contiene funciones y variables globales
 */
const SmartWatts = {
    
    /**
     * Inicializar la aplicación
     */
    init: function() {
        this.setupEventListeners();
        this.setupWebSockets();
        this.setupAutoRefresh();
        this.setupTopbarDate();
        this.setupSortableTables();
    },

    /**
     * Configurar event listeners
     */
    setupEventListeners: function() {
        // Toggle de sidebar en móvil
        const sidebarToggle = document.getElementById('sidebarToggle');
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.getElementById('sidebarOverlay');

        if (sidebarToggle && sidebar && overlay) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            });

            // Cerrar sidebar al hacer click en el overlay
            overlay.addEventListener('click', function() {
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
            });

            // Cerrar sidebar al seleccionar un enlace (móvil)
            sidebar.querySelectorAll('.nav-link, .sidebar-logout').forEach(link => {
                link.addEventListener('click', function() {
                    sidebar.classList.remove('active');
                    overlay.classList.remove('active');
                });
            });
        }

        // Descartar alertas automáticamente
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                const closeBtn = alert.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.click();
                }
            }, 5000);
        });
    },

    /**
     * Mostrar la fecha actual en el topbar
     */
    setupTopbarDate: function() {
        const dateEl = document.getElementById('topbar-date');
        if (dateEl) {
            const opciones = { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' };
            dateEl.textContent = new Date().toLocaleDateString('es-ES', opciones);
        }
    },

    /**
     * Habilitar el ordenamiento de columnas en tablas marcadas
     * con la clase "table-sortable"
     */
    setupSortableTables: function() {
        document.querySelectorAll('table.table-sortable').forEach(table => {
            const headers = table.querySelectorAll('thead th[data-sort]');
            headers.forEach(th => {
                th.classList.add('sortable-header');
                th.innerHTML += ' <i class="fas fa-sort sort-icon"></i>';
                th.addEventListener('click', function() {
                    SmartWatts.sortTableByColumn(table, th, headers);
                });
            });
        });
    },

    /**
     * Ordenar las filas de una tabla según la columna seleccionada
     */
    sortTableByColumn: function(table, th, headers) {
        const allHeaders = Array.from(table.querySelectorAll('thead th'));
        const colIndex = allHeaders.indexOf(th);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const currentDir = th.getAttribute('data-sort-dir') || 'none';
        const newDir = currentDir === 'asc' ? 'desc' : 'asc';

        // Reiniciar iconos y estado de las demás columnas
        headers.forEach(h => {
            h.removeAttribute('data-sort-dir');
            h.classList.remove('sort-active');
            const icon = h.querySelector('.sort-icon');
            if (icon) icon.className = 'fas fa-sort sort-icon';
        });

        th.setAttribute('data-sort-dir', newDir);
        th.classList.add('sort-active');
        const icon = th.querySelector('.sort-icon');
        if (icon) icon.className = `fas fa-sort-${newDir === 'asc' ? 'up' : 'down'} sort-icon`;

        rows.sort((a, b) => {
            const aText = (a.children[colIndex].textContent || '').trim();
            const bText = (b.children[colIndex].textContent || '').trim();

            const aNum = parseFloat(aText.replace(/[^0-9.,-]/g, '').replace(',', '.'));
            const bNum = parseFloat(bText.replace(/[^0-9.,-]/g, '').replace(',', '.'));

            let cmp;
            if (!isNaN(aNum) && !isNaN(bNum) && aText.match(/^[\s\d.,$%-]+$/) && bText.match(/^[\s\d.,$%-]+$/)) {
                cmp = aNum - bNum;
            } else {
                cmp = aText.localeCompare(bText, 'es', { sensitivity: 'base' });
            }

            return newDir === 'asc' ? cmp : -cmp;
        });

        rows.forEach(row => tbody.appendChild(row));
    },
    
    /**
     * Configurar WebSockets para comunicación en tiempo real
     */
    setupWebSockets: function() {
        // Solo si hay un elemento socket disponible
        if (typeof socket === 'undefined') {
            return;
        }
        
        // Conectar a Socket.IO
        socket.on('connect', function() {
            console.log('Conectado a servidor WebSocket');
        });
        
        socket.on('disconnect', function() {
            console.log('Desconectado del servidor WebSocket');
        });
        
        // Escuchar notificaciones en tiempo real
        socket.on('nueva_notificacion', function(data) {
            SmartWatts.mostrarNotificacion(data);
            SmartWatts.actualizarBadgeNotificaciones();
        });
        
        // Escuchar actualizaciones de datos
        socket.on('datos_actualizados', function(data) {
            SmartWatts.actualizarDashboard(data);
        });
    },
    
    /**
     * Mostrar notificación en pantalla
     */
    mostrarNotificacion: function(data) {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-info alert-dismissible fade show';
        alertDiv.setAttribute('role', 'alert');
        
        let iconClass = 'fa-info-circle';
        if (data.tipo === 'consumo') {
            alertDiv.className = 'alert alert-warning alert-dismissible fade show';
            iconClass = 'fa-exclamation-triangle';
        } else if (data.tipo === 'presupuesto') {
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            iconClass = 'fa-bell';
        } else if (data.tipo === 'dispositivo') {
            alertDiv.className = 'alert alert-info alert-dismissible fade show';
            iconClass = 'fa-plug';
        }
        
        alertDiv.innerHTML = `
            <i class=\"fas ${iconClass}\"></i> ${data.mensaje}
            <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"alert\"></button>
        `;
        
        // Insertar al inicio del contenido
        const content = document.querySelector('.content-area');
        if (content) {
            content.insertBefore(alertDiv, content.firstChild);
            
            // Remover automáticamente después de 5 segundos
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    },
    
    /**
     * Actualizar badge de notificaciones
     */
    actualizarBadgeNotificaciones: function() {
        fetch('/notificaciones/api/sin-leer')
            .then(response => response.json())
            .then(data => {
                const badge = document.getElementById('notificacion-badge');
                if (badge) {
                    badge.style.display = data.cantidad > 0 ? 'block' : 'none';
                }
            })
            .catch(err => console.error('Error actualizando notificaciones:', err));
    },
    
    /**
     * Actualizar datos del dashboard
     */
    actualizarDashboard: function(data) {
        console.log('Actualizando dashboard con:', data);
        
        // Actualizar valores de elementos
        if (data.potencia_total !== undefined) {
            const elem = document.querySelector('[data-potencia]');
            if (elem) elem.textContent = data.potencia_total.toFixed(2) + ' W';
        }
        
        if (data.consumo_hoy !== undefined) {
            const elem = document.querySelector('[data-consumo]');
            if (elem) elem.textContent = data.consumo_hoy.toFixed(3) + ' kWh';
        }
    },
    
    /**
     * Configurar actualización automática de datos
     */
    setupAutoRefresh: function() {
        // Actualizar notificaciones cada 30 segundos
        setInterval(() => {
            SmartWatts.actualizarBadgeNotificaciones();
        }, 30000);
        
        // Actualizar dashboard cada 60 segundos
        const chartElement = document.getElementById('chartConsumo24h');
        if (chartElement) {
            setInterval(() => {
                SmartWatts.refrescarGraficos();
            }, 60000);
        }
    },
    
    /**
     * Refrescar gráficos de datos
     */
    refrescarGraficos: function() {
        // Obtener nuevos datos
        fetch('/api/grafico-consumo/dia')
            .then(response => response.json())
            .then(data => {
                console.log('Datos de gráfico actualizados:', data);
                // Aquí se actualizarían los gráficos Chart.js
            })
            .catch(err => console.error('Error actualizando gráficos:', err));
    },
    
    /**
     * Mostrar modal de confirmación
     */
    confirmar: function(mensaje, callback) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class=\"modal-dialog\">
                <div class=\"modal-content\">
                    <div class=\"modal-header\">
                        <h5 class=\"modal-title\">Confirmar</h5>
                        <button type=\"button\" class=\"btn-close\" data-bs-dismiss=\"modal\"></button>
                    </div>
                    <div class=\"modal-body\">
                        ${mensaje}
                    </div>
                    <div class=\"modal-footer\">
                        <button type=\"button\" class=\"btn btn-secondary\" data-bs-dismiss=\"modal\">
                            Cancelar
                        </button>
                        <button type=\"button\" class=\"btn btn-primary\" id=\"confirmBtn\">
                            Confirmar
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        
        document.getElementById('confirmBtn').addEventListener('click', function() {
            bsModal.hide();
            callback();
            modal.remove();
        });
        
        bsModal.show();
    },
    
    /**
     * Marcar notificación como leída
     */
    marcarNotificacionLeida: function(notificacionId) {
        fetch(`/notificaciones/${notificacionId}/marcar-leida`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            SmartWatts.actualizarBadgeNotificaciones();
        })
        .catch(err => console.error('Error marcando notificación:', err));
    },
    
    /**
     * Eliminar notificación
     */
    eliminarNotificacion: function(notificacionId) {
        SmartWatts.confirmar('¿Eliminar esta notificación?', function() {
            fetch(`/notificaciones/${notificacionId}/eliminar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                SmartWatts.actualizarBadgeNotificaciones();
                location.reload();
            })
            .catch(err => console.error('Error eliminando notificación:', err));
        });
    },
    
    /**
     * Eliminar dispositivo
     */
    eliminarDispositivo: function(dispositivoId) {
        SmartWatts.confirmar('¿Eliminar este dispositivo?', function() {
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/dispositivos/${dispositivoId}/eliminar`;
            document.body.appendChild(form);
            form.submit();
        });
    },
    
    /**
     * Copiar token a portapapeles
     */
    copiarAlPortapapeles: function(texto) {
        navigator.clipboard.writeText(texto).then(function() {
            alert('Token copiado al portapapeles');
        }).catch(function(err) {
            console.error('Error copiando:', err);
        });
    },
    
    /**
     * Formatear números como moneda
     */
    formatearMoneda: function(valor) {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS'
        }).format(valor);
    },
    
    /**
     * Formatear números con decimales
     */
    formatearDecimal: function(valor, decimales = 2) {
        return parseFloat(valor).toFixed(decimales);
    }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    SmartWatts.init();
});
