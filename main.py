# EgoYa4
# Task 4

import gooeypie as gp
import csv
from operator import itemgetter, attrgetter

orders = []     # list of customer orders, each item is a dict
vans = {}       # dict of van types

# dict for delivery information
delivery = {'VIC': {'cost': 0, 'inst': 'Heidelberg showroom pickup'},
            'TAS': {'cost': 0, 'inst': 'Purchasers are required to book their own freight on the Spirit of Tasmania'},
            'SA': {'cost': 1000, 'inst': 'Adelaide showroom pickup'},
            'NSW': {'cost': 1500, 'inst': 'Sydney showroom pickup'},
            'QLD': {'cost': 2500, 'inst': 'Brisbane showroom pickup'},
            'WA': {'cost': 4500, 'inst': 'Perth showroom pickup'},
            'NT': {'cost': 3500, 'inst': 'Darwin showroom pickup'}
            }


# load caravan data from csv file
# file format: name, batMax, battSupp, price
def loadVanDataFromFile():
    try:
        fieldheaders = ['name', 'batMax', 'batSupp', 'price']
        with open('EgoYaVans.csv', newline='') as f:
            for row in csv.DictReader(f, fieldheaders):
                vans[row['name']] = row     # add van data to dict, using name as key
    except:
        print('No caravan data file!')
        exit()

# load orders list from orders file
# file format: lastName, firstName, phone, vanType, extraBat, delivState, price
def loadOrdersFromFile():
    try:
        fieldheaders = ['lastName', 'firstName', 'phone', 'vanType', 'extraBat', 'delivState', 'price']
        with open('vanOrders.csv', newline='') as f:
            for row in csv.DictReader(f, fieldheaders):
                orders.append(row)
    except:
        print('No customers file!')


def saveOrdersToFile():
    with open('vanOrders.csv', 'w', newline='') as csvfile:
        fieldnames = ['lastName', 'firstName', 'phone', 'vanType', 'extraBat', 'delivState', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        for order in orders:
            writer.writerow(order)
    return True     # success, can exit app

def calculateVanCost(vanType, batExtra):
    vanData = vans[vanType]     # extract data for selected van
    totalPrice = int(vanData['price'])    # add base price to total
    totalPrice += batExtra * 495        # calculate total van price including extra batteries

    return totalPrice

# handles GUI updates   - all fields and menus must have data selected to enable Confirm Order button
#                       - also sets delivery state info as needed
def updateUI(event):
    if lastNameEntry.text and firstNameEntry.text and phoneEntry.text and caravanMenu.selected and batteriesMenu.selected and stateMenu.selected:
        confirmBtn.disabled = False
    else:
        confirmBtn.disabled = True

    if event.widget == stateMenu:                   # if delivery state changed, update the delivery info message
        deliveryInfo.text = delivery[stateMenu.selected]['inst']


# this checks to see that the maximum number of batteries have not been exceeded for a particular model of caravan
# if too many batteries selected, show error message and return False
# if all data present return True
def checkMaximumBatteries(vanType, extraBatteries):
    if int(vans[vanType]['batSupp']) + extraBatteries > int(vans[vanType]['batMax']):
        app.alert('Maximum batteries exceeded', 'That many batteries cannot be selected for this caravan', 'warning')
        return False
    else:
        return True

# this checks that fields are filled and popups selected
# if data is missing return False
# if all data present return True
def allDataEntered():
    if caravanMenu.selected and batteriesMenu.selected and stateMenu.selected and lastNameEntry.text and firstNameEntry.text and phoneEntry.text:
        return True
    else:
        return False

def confirmOrder(event):
    while not allDataEntered():         # check all fields and dropdown menus have been chosen
        app.alert('Some data is missing', 'Please enter all required data', 'warning')
        return

    vanType = caravanMenu.selected
    batExtra = int(batteriesMenu.selected)

    if not checkMaximumBatteries(vanType, batExtra):
        return                          # if too many batteries are selected, exit without completing order

    totalPrice = calculateVanCost(vanType, int(batExtra))
    # set total price field in GUI
    priceResult.text = '$' + str(totalPrice)

    order={}
    order['lastName'] = lastNameEntry.text
    order['firstName'] = firstNameEntry.text
    order['phone'] = phoneEntry.text
    order['vanType'] = vanType
    order['extraBat'] = batExtra
    order['delivState'] = stateMenu.selected
    order['price'] = totalPrice

    # add this order to orders list
    orders.append(order)


# print list of all orders, sorted by customer surname
# bug: lower-case first letter will sort after 'Z'
def sortCustomers(event):
    orderSorted = sorted(orders, key=itemgetter('lastName'))
    for customer in orderSorted:
        print(','.join(customer.values()))      # print comma-delimited list of customer record

# print list of all orders for specified caravan type (set by caravanMenu selection)
def filterByVan(event):
    # get vanType from selection popup
    vanType = caravanMenu.selected
    # find sublist of orders that have vanType
    filterList = []
    for order in orders:
        if order['vanType'] == vanType:
            filterList.append(order)

    print(f'Orders for {vanType}:')
    for order in filterList:
        print(','.join(order.values()))         # print comma-delimited list of selected orders

# MAIN PROGRAM STARTS HERE

# read customer orders in csv format, loads into orders[]
loadOrdersFromFile()

# read caravan data in csv format, loads into vans{}
loadVanDataFromFile()

# Caravan info is a dictionary, with a key for the van type
# and value is a dictionary containing
# name:[max batteries, batteries supplied, price]

caravans = ['UC', 'Buckley', 'Plenty', 'Ridge']
batteries = [0, 1, 2]
states = ['VIC', 'TAS', 'SA', 'NSW', 'QLD', 'NT', 'WA']

# BEGIN USER INTERFACE

app = gp.GooeyPieApp('EgoYa Caravans Orders')

app.on_close(saveOrdersToFile)      # save orders on window close and exit

app.width = 250

app.set_grid(8, 8)

# first two columns are customer info and labels
firstNameLabel = gp.Label(app, 'First Name')
firstNameEntry = gp.Input(app)
firstNameEntry.justify = 'left'
firstNameEntry.width = 20
firstNameEntry.add_event_listener('blur', updateUI)

lastNameLabel = gp.Label(app, 'Last Name')
lastNameEntry = gp.Input(app)
lastNameEntry.justify = 'left'
lastNameEntry.width = 20
lastNameEntry.add_event_listener('blur', updateUI)

phoneLabel = gp.Label(app, 'Phone')
phoneEntry = gp.Input(app)
phoneEntry.justify = 'left'
phoneEntry.width = 20
phoneEntry.add_event_listener('blur', updateUI)

# next two columns are caravan info and labels

caravanLabel = gp.Label(app, 'Choose caravan:')
caravanMenu = gp.Dropdown(app, caravans)
caravanMenu.width = 10
caravanMenu.add_event_listener('select', updateUI)

batteriesLabel = gp.Label(app, 'Extra batteries:')
batteriesMenu = gp.Dropdown(app, batteries)
batteriesMenu.width = 10
batteriesMenu.add_event_listener('select', updateUI)

stateLabel = gp.Label(app, 'Delivery state:')
stateMenu = gp.Dropdown(app, states)
stateMenu.width = 10
stateMenu.add_event_listener('select', updateUI)

deliveryLabel = gp.Label(app, 'Delivery instructions:')
deliveryInfo = gp.Label(app, '')

priceLabel = gp.Label(app, 'Final cost:')
priceResult = gp.Label(app, '$0')

surnameBtn = gp.Button(app, 'Surname Sort', sortCustomers)

filterBtn = gp.Button(app, 'Filter by Van', filterByVan)

confirmBtn = gp.Button(app, 'Confirm Order', confirmOrder)
confirmBtn.disabled = True

# elements added in (row, column) order
app.add(firstNameLabel, 1, 1, align='right')
app.add(firstNameEntry, 1, 2, align='center')
app.add(lastNameLabel, 2, 1, align='right')
app.add(lastNameEntry, 2, 2, align='center')
app.add(phoneLabel, 3, 1, align='right')
app.add(phoneEntry, 3, 2, align='center')

app.add(caravanLabel, 1, 3, align='center')
app.add(caravanMenu, 1, 4, align='center')
app.add(batteriesLabel, 2, 3, align='center')
app.add(batteriesMenu, 2, 4, align='center')
app.add(stateLabel, 3, 3, align='center')
app.add(stateMenu, 3, 4, align='center')

app.add(surnameBtn, 1, 5, align='center')
app.add(filterBtn, 2, 5, align='center')

app.add(priceLabel, 4, 1, align='right')
app.add(priceResult, 4, 2, align='left')

app.add(deliveryLabel, 5, 1, align='right')
app.add(deliveryInfo, 5, 2, align='left', column_span=4)

app.add(confirmBtn, 6, 5, align='center')

app.run()

exit()
