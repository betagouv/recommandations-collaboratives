import Alpine from 'alpinejs'
import List from 'list.js'

Alpine.data("SearchableList", SearchableList)

function SearchableList(listId, listCount, searchParams) {

    return {
        selectedList: [],
        onFocus:false,
        init() {

            if (!listCount > 0) return

            const options = {
                valueNames: ['name']
            };

            new List(listId, options);
            
            //Get already selected items
            Array.from(this.$refs.defaultField.children[listId].options).forEach(option => {
                if (option.selected) {
                    const selectedItem = {
                        name: option.innerHTML,
                        value: option.value,
                        element: option
                    }
                    this.selectedList.push(selectedItem);
                }
            })

            Array.from(this.$refs.selectList.children).forEach(li => {
                this.selectedList.forEach(item => {
                    if (li.getAttribute("id") == item.value) {
                        li.classList.add('d-none')
                    }
                })
            })
        },
        handleFocusList() {
            return this.onFocus = true
        },
        handleBlurList(event) {
            setTimeout(() => {
                return this.onFocus = false
            }, 100);
        },
        handleAddItem(event, value, name) {
            event.target.parentNode.classList.add('d-none')
            const selectedItem = {
                name: name,
                value: value,
                element: event.target.parentNode
            }
            this.selectedList.push(selectedItem);

            Array.from(this.$refs.defaultField.children[listId].options).forEach(option => {
                if (option.value == value) {
                    option.selected = true
                }
            })
        },
        handleRemoveItem(event, el) {
            const removedItem = this.selectedList.find(item => item.value == el.value);
            removedItem.element.classList.remove('d-none')

            event.target.parentNode.classList.remove('d-none')
            const itemFound = this.selectedList.indexOf(el)
            this.selectedList.splice(itemFound, 1)

            Array.from(this.$refs.defaultField.children[listId].options).forEach(option => {
                if (option.value == el.value) {
                    option.selected = false
                }
            })
        }
    }
}

