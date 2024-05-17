from gpt_engineer.api.engine import split_blocks_by_gt_lt

changes_example = """Sure, here is a list of files to be modified along with the changes needed:

<GPT_CODE_CHANGE>
FILE: /shared/onwaytransfers.com/dev/owt/OWTB2BDashboard/src/components/search/Booker.vue
CHANGES: 
- Update the `data` object to include fields required for the API booking request.
- Modify the `bookTrip` method to construct the booking request JSON object as per the API requirements.
- Ensure all necessary fields are captured in the form and mapped correctly to the booking request.

Details:
1. Add fields for `agency_ref`, `contract_line_id`, `sale_currency`, `adults`, `children`, `infants`, `booster_seats`, `baby_seats`, `luggage`, `pickup_datetime`, `pickup_address`, `dropoff_address`, `inward_terminal_datetime`, `outward_terminal_datetime`, `inward_flight_service_ref`, `outward_flight_service_ref`, and `client_locale`.
2. Update the form to capture these fields if they are not already present.
3. Modify the `bookTrip` method to create a JSON object that matches the API booking request format.

Example:
```javascript
data() {
  return {
    currentStep: 1,
    breadcrumbs: [
      { text: 'Passenger Details', icon: 'fa-user' },
      { text: 'Flight Details', icon: 'fa-plane' },
      { text: 'Payment', icon: 'fa-credit-card' }
    ],
    trip: {
      from: 'Cascades Les Halles, Paris, Rue des Innocents, Paris, France',
      to: 'CDG - Paris, FR - Paris Charles De Gaulle Airport',
      carbonOffset: false,
    },
    passenger: {
      firstName: '',
      lastName: '',
      email: '',
      emailConfirmation: '',
      countryCode: 'United States (+1)',
      phoneNumber: '',
      specialInstructions: '',
      password: '',
    },
    notifications: {
      sms: false,
    },
    flight: {
      number: '',
      pickupTime: '10:00 AM',
    },
    upgrade: {
      gratuity: '0',
    },
    payment: {
      coupon: '',
      cardNumber: '',
      cardholderName: '',
      expirationDate: '',
      cvv: '',
      cancellationPolicy: 'standard',
      marketingEmails: false,
    },
    agency_ref: 'MNX-PLZ-4444444', // Example value, should be dynamically set
    contract_line_id: 44084, // Example value, should be dynamically set
    sale_currency: 'USD', // Example value, should be dynamically set
    adults: 1, // Example value, should be dynamically set
    children: 1, // Example value, should be dynamically set
    infants: 0, // Example value, should be dynamically set
    booster_seats: 1, // Example value, should be dynamically set
    baby_seats: 0, // Example value, should be dynamically set
    luggage: 3, // Example value, should be dynamically set
    pickup_datetime: '2023-12-23T03:50:00', // Example value, should be dynamically set
    pickup_address: 'Via del Sudario, 27\r\n00186 Roma RM\r\nItaly', // Example value, should be dynamically set
    dropoff_address: 'FCO airport', // Example value, should be dynamically set
    inward_terminal_datetime: null, // Example value, should be dynamically set
    outward_terminal_datetime: '2023-12-23T06:55', // Example value, should be dynamically set
    inward_flight_service_ref: null, // Example value, should be dynamically set
    outward_flight_service_ref: 'vy6210', // Example value, should be dynamically set
    client_locale: 'es' // Example value, should be dynamically set
  };
},
methods: {
  bookTrip() {
    const bookingRequest = {
      agency_ref: this.agency_ref,
      contract_line_id: this.contract_line_id,
      passenger_name: `${this.passenger.firstName} ${this.passenger.lastName}`,
      passenger_phone: this.passenger.phoneNumber,
      passenger_email: this.passenger.email,
      sale_currency: this.sale_currency,
      adults: this.adults,
      children: this.children,
      infants: this.infants,
      booster_seats: this.booster_seats,
      baby_seats: this.baby_seats,
      luggage: this.luggage,
      comments_visible: this.passenger.specialInstructions,
      pickup_datetime: this.pickup_datetime,
      from: this.trip.from,
      to: this.trip.to,
      pickup_address: this.pickup_address,
      dropoff_address: this.dropoff_address,
      inward_terminal_datetime: this.inward_terminal_datetime,
      outward_terminal_datetime: this.outward_terminal_datetime,
      inward_flight_service_ref: this.inward_flight_service_ref,
      outward_flight_service_ref: this.flight.number,
      client_locale: this.client_locale
    };

    console.log('Booking trip with details:', bookingRequest);
    // Add the booking logic here, e.g., making an API call
  },
  signIn() {
    console.log('Signing in...');
    // Add sign-in logic here
  },
  nextStep() {
    if (this.currentStep < this.breadcrumbs.length) {
      this.currentStep++;
    }
  },
  prevStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
    }
  },
  navigateToStep(step) {
    this.currentStep = step;
  }
}
```
</GPT_CODE_CHANGE>


<GPT_CODE_CHANGE>
FILE: /shared/onwaytransfers.com/dev/owt/OWTWiki/wiki/departments/engineering/projects/api/index.md
CHANGES: 
- Update the documentation to reflect the changes in the `CreateBooking` API request.
- Ensure the sample request and request model are up-to-date with the new fields and structure.

Details:
1. Add fields for `agency_ref`, `contract_line_id`, `sale_currency`, `adults`, `children`, `infants`, `booster_seats`, `baby_seats`, `luggage`, `pickup_datetime`, `pickup_address`, `dropoff_address`, `inward_terminal_datetime`, `outward_terminal_datetime`, `inward_flight_service_ref`, `outward_flight_service_ref`, and `client_locale` in the `CreateBooking` section.
2. Update the sample request to include these fields.

Example:
```md
## CreateBooking

Using the full set of available data, as long as they validate, this operation generates a booking in the OWT 
system and delivers a service request to the supplier (based on the chosen contract line).
The client_locale field will translate the response if the x-owtlocale header is not present.

**Method**: POST

**URL**: /api/CreateBooking

Sample Request:
```JSON
  {
    "agency_ref": "MNX-PLZ-4444444",
    "contract_line_id": 44084,
    "passenger_name": "Mr B. Travellin",
    "passenger_phone": "+447893985723",
    "passenger_email": "btravellin@test.com",
    "sale_currency": "usd",
    "adults": 1,
    "children": 1,
    "infants": 0,
    "booster_seats": 1,
    "baby_seats": 0,
    "luggage": 3,
    "comments_visible": "wear a pink carnation so I can recognise you.",
    "pickup_datetime": "2023-12-23T03:50:00",
    "from": "[41.89596,12.47566]",
    "to": "FCO",
    "pickup_address": "Via del Sudario, 27\r\n00186 Roma RM\r\nItaly",
    "dropoff_address": "FCO airport",
    "inward_terminal_datetime": null,
    "outward_terminal_datetime": "2023-12-23T06:55",
    "inward_flight_service_ref": null,
    "outward_flight_service_ref": "vy6210",
    "client_locale": "es"
  }
```
Request Model:
- **agency_ref** (string) **required**: 
the identifier applied to the booking by the agency entity sending the 
request
- **contract_line_id**
(int)
required
the identifier for the contract line select from the availability search query
- **passenger_name**
(string)
required
name of the lead passenger
- **passenger_phone**
(string)
phone number for the lead passenger
at least 1
- **passenger_email** required
(string)
email address for the lead passenger
- **sale_currency**
(string)
required
3 letter ISO currency code for the sale (case insensitive)
- **adults**
(int)
number of passengers that are adults
at least 1
- **children** required
(int)
number of passengers that are children
- **infants**
(int)
number of passengers that are infants
- **booster_seats**
(int)
quantity of booster seats to request
- **baby_seats**
(int)
quantity of baby seats to request
- **luggage**
(int)
quantity of suitcases required to be transported
- **comments_visible**
(string)
additional information to include with the booking for the service provider
- **pickup_datetime**
(datetime string)
required
the date & time to order for pickup
from required
```
</GPT_CODE_CHANGE>
"""

def test_section_splitter_gt_lt():
 
  blocks = list(split_blocks_by_gt_lt(changes_example))
  assert len(blocks) == 2
  assert blocks[0][0] == "FILE: /shared/onwaytransfers.com/dev/owt/OWTB2BDashboard/src/components/search/Booker.vue"
  assert blocks[1][0] == "FILE: /shared/onwaytransfers.com/dev/owt/OWTWiki/wiki/departments/engineering/projects/api/index.md"
