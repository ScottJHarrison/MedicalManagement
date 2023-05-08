function displayTimeSlots() {
    $.get('/timetable', function (data) {
        let timeSlotsTableBody = $('#time-slots-table tbody');
        timeSlotsTableBody.empty();

        data.forEach(function (slot) {
            let slotRow = $('<tr>');
            slotRow.append(`<td>${slot.doctor_id}</td>`);
            slotRow.append(`<td>${slot.patient_id}</td>`);
            slotRow.append(`<td>${slot.date}</td>`);
            slotRow.append(`<td>${slot.start_time}</td>`);
            slotRow.append(`<td>${slot.end_time}</td>`);
            slotRow.append(`<td>${slot.status}</td>`);
            slotRow.append(`<td><button class="edit-btn" data-id="${slot._id}">Edit</button> <button class="delete-btn" data-id="${slot._id}">Delete</button></td>`);
            timeSlotsTableBody.append(slotRow);
        });
    });
}

$(document).ready(function () {
    displayTimeSlots();

    // Handle form submission to add a new time slot
    $('#add-time-slot-form').on('submit', function (event) {
        event.preventDefault();

        let formData = {
            doctor_id: $('#doctor_id').val(),
            patient_id: $('#patient_id').val(),
            date: $('#date').val(),
            start_time: $('#start_time').val(),
            end_time: $('#end_time').val(),
            status: $('#status').val()
        };

        $.ajax({
            type: 'POST',
            url: '/timetable/add',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function (response) {
                displayTimeSlots();
                $('#add-time-slot-form')[0].reset();
            },
            error: function (response) {
                alert('An error occurred while adding the time slot. Please try again.');
            }
        });
    });

   $('#time-slots-table').on('click', '.edit-btn', function () {
    let slotId = $(this).data('id');
    let row = $(this).closest('tr');

    // Load time slot data
    $.get('/timetable/' + slotId, function (data) {
        // Populate the edit form with the current time slot data
        $('#edit-doctor_id').val(data.doctor_id);
        $('#edit-patient_id').val(data.patient_id);
        $('#edit-date').val(data.date);
        $('#edit-start_time').val(data.start_time);
        $('#edit-end_time').val(data.end_time);
        $('#edit-status').val(data.status);
        $('#edit-slot_id').val(slotId);

        // Show the edit form
        $('#edit-time-slot-container').show();
    });
});

// Handle form submission to edit an existing time slot
$('#edit-time-slot-form').on('submit', function (event) {
    event.preventDefault();

    let slotId = $('#edit-slot_id').val();
    let formData = {
        doctor_id: $('#edit-doctor_id').val(),
        patient_id: $('#edit-patient_id').val(),
        date: $('#edit-date').val(),
        start_time: $('#edit-start_time').val(),
        end_time: $('#edit-end_time').val(),
        status: $('#edit-status').val()
    };

    $.ajax({
        type: 'PUT',
        url: '/timetable/update/' + slotId,
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function (response) {
            displayTimeSlots();

            // Hide the edit form
            $('#edit-time-slot-container').hide();
        },
        error: function (response) {
            alert('An error occurred while updating the time slot. Please try again.');
        }
    });
});


    // Handle delete button click
    $('#time-slots-table').on('click', '.delete-btn', function () {
        let slotId = $(this).data('id');

        $.ajax({
            type: 'DELETE',
            url: '/timetable/delete/' + slotId,
            success: function (response) {
                displayTimeSlots();
            },
            error: function (response) {
                alert('An error occurred while deleting the time slot. Please try again.');
            }
        });
    });

    // Handle form submission to edit an existing time slot
    // ...
});

// Initialize the FullCalendar
function initializeCalendar() {
  $("#calendar").fullCalendar({
    header: {
      left: "prev,next today",
      center: "title",
      right: "month,agendaWeek,agendaDay",
    },
    events: function (start, end, timezone, callback) {
      $.get("/timetable", function (data) {
        let events = data.map(function (slot) {
          return {
            title: `Doctor: ${slot.doctor_id}, Patient: ${slot.patient_id}`,
            start: `${slot.date}T${slot.start_time}`,
            end: `${slot.date}T${slot.end_time}`,
          };
        });
        callback(events);
      });
    },
  });
}

// Update this function
$(document).ready(function () {
  displayTimeSlots();
  initializeCalendar();

});

//testing

$(document).ready(function () {
    // Other code ...

    // Handle form submission to submit a request
    $("#request-form").submit(function (event) {
  event.preventDefault();

  const name = $("#name").val();
  const requestType = $("#request_type").val();
  const requestDetails = $("#request_details").val();

  $.ajax({
    url: "/submit_request",
    type: "POST",
    data: {
      name: name,
      request_type: requestType,
      request_details: requestDetails,
    },
    success: function (response) {
      alert("Request submitted successfully!");
      $("#request-form")[0].reset();
    },
    error: function (error) {
      console.error(error);
      alert("There was an error submitting the request.");
    },
  });
});
});

const token = '';

//#############################################################################
$(document).ready(function () {
  $('.slider').slick({
    autoplay: true,
    autoplaySpeed: 2500,
    arrows: false,
    dots: true,
  });
});

//##############################################################################

function submitReview(event) {
    event.preventDefault();
    const name = document.getElementById("name").value;
    const stars = document.getElementById("stars").value;
    const review = document.getElementById("review").value;

    fetch("/submit_review", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name: name,
        stars: stars,
        review: review,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          document.getElementById("name").value = "";
          document.getElementById("stars").value = "";
          document.getElementById("review").value = "";
          loadReviews();
        } else {
          console.error("Error submitting review:", data.message);
        }
      })
      .catch((error) => {
        console.error("Error submitting review:", error);
      });
      loadReviews();
      document.addEventListener("DOMContentLoaded", loadReviews);
  }

   function loadReviews() {
    fetch("/load_reviews")
      .then((response) => response.json())
      .then((reviews) => {
        const reviewsList = document.getElementById("reviews-list");
        reviewsList.innerHTML = "";
        reviews.forEach((review) => {
          const listItem = document.createElement("li");
          listItem.innerHTML = `<strong>${review.name}</strong> - ${review.stars} Stars<br>${review.review}`;
          reviewsList.appendChild(listItem);
        });
      })
      .catch((error) => {
        console.error("Error loading reviews:", error);
      });
  }

  // TEST TEST TEST

async function filterRecords() {
  const searchInput = document.getElementById("search-input");
  const searchQuery = searchInput.value.trim().toLowerCase();

  const response = await fetch("/get_patient_records");
  const records = await response.json();

  const filteredRecords = records.filter((record) => {
    const values = Object.values(record);
    return values.some((value) => value.toString().toLowerCase().includes(searchQuery));
  });

  displaySearchResults(filteredRecords);
}

function displaySearchResults(records) {
  const searchResultsContainer = document.getElementById("search-results-container");
  searchResultsContainer.innerHTML = "";

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  // Table Head
  const trHead = document.createElement("tr");
  const headings = ["Date", "Patient ID", "Gender", "Age", "SAT Score", "First Initial", "Last Name", "Race", "Admin Flag", "Wait Time", "Department Referral"];
  headings.forEach((heading) => {
    const th = document.createElement("th");
    th.innerText = heading;
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);
  table.appendChild(thead);

  // Table Body
  records.forEach((record) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${record.date}</td>
      <td>${record.patient_id}</td>
      <td>${record.patient_gender}</td>
      <td>${record.patient_age}</td>
      <td>${record.patient_sat_score}</td>
      <td>${record.patient_first_inital}</td>
      <td>${record.patient_last_name}</td>
      <td>${record.patient_race}</td>
      <td>${record.patient_admin_flag}</td>
      <td>${record.patient_waittime}</td>
      <td>${record.department_referral}</td>
    `;
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  searchResultsContainer.appendChild(table);
}
