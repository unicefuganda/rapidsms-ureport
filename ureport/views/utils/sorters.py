class ContactsViewSorter(object):
    def sort(self, column, object_list, ascending=True):
        query = "select id,%s from contacts_export order by %s" % ('asc' if ascending else 'desc', column,column)
        return object_list.raw(query)