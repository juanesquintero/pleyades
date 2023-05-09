/////////////////////////////////// SIDE BAR /////////////////////////////////
// Hide submenus
$('#body-row .collapse').collapse('hide');

// Collapse/Expand icon
$('#collapse-icon').addClass('fa-angle-double-left');

// Collapse click
$('[data-toggle=sidebar-colapse]').click(function () {
    SidebarCollapse();
});

function SidebarCollapse() {
    $('.menu-collapsed').toggleClass('d-none');
    $('.sidebar-submenu').toggleClass('d-none');
    $('.submenu-icon').toggleClass('d-none');
    $('#sidebar-container').toggleClass('sidebar-expanded sidebar-collapsed');

    // Treating d-flex/d-none on separators with title
    let SeparatorTitle = $('.sidebar-separator-title');
    if (SeparatorTitle.hasClass('d-flex')) {
        SeparatorTitle.removeClass('d-flex');
    } else {
        SeparatorTitle.addClass('d-flex');
    }

    // Collapse/Expand icon
    $('#collapse-icon').toggleClass('fa-angle-double-left fa-angle-double-right');
}
/////////////////////////////////// END SIDE BAR /////////////////////////////////

//Titulo alt en input de acciones 
$(function () {
    $('[data-toggle="tooltip"]').tooltip()
})

// Script para filtrar y ordenar tablas 
$(document).ready(function () {
    $("#filtroTabla").on("keyup", function () {
        let value = $(this).val().toLowerCase();
        $("#tabla tbody tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});


// ordenar por columna
// function sortTable(column) {
//     let table = $('table');
//     console.log(table);
//     let rows = $('tbody > tr', table);

//     rows.sort(function (a, b) {
//         let keyA = $('td.' + column, a).text().toUpperCase();
//         let keyB = $('td.' + column, b).text().toUpperCase();

//         if (keyA < keyB) return -1;
//         if (keyA > keyB) return 1;
//         return 0;
//     });

//     $.each(rows, function (index, row) {
//         table.append(row);
//     });
// }


// $('.sortable').click(function () {
//     let column = $(this).data('sort');
//     sortTable(column);
// });


