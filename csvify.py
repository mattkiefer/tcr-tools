from csvkit.utilities.in2csv import In2CSV

def csvify(file_path=None,add_args=None):
    """
    wrapper to convert
    spreadsheet to csv file
    with optional args
    """
    # naming stuff
    file_dir = '/'.join(file_path.split('/')[:-1]) + '/'
    file_name = file_path.split('/')[-1]
    file_ext = file_name.split('.')[-1]
    #output_file_path = file_dir + file_name.replace(file_ext,'csv')
    output_file_path = file_name.replace(file_ext,'csv')
    output_file = open(output_file_path,'w')
    
    # conversion
    args = [file_path,'--format='+file_ext,'--no-inference']
    if add_args:
        args = args + add_args
    util = In2CSV(args=args,output_file=output_file)
    util.main()
    output_file.close()
    return output_file_path
