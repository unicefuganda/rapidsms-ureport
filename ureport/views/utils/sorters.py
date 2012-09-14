class ContactsViewSorter(object):
    def sort(self, column, object_list, ascending=True):
        query = "select id,%s from contacts_export order by %s %s" % ( column,column,'asc' if ascending else 'desc')
        return object_list.raw(query)