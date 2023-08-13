**To delete the tag sets of an object**

The following ``delete-object-tagging`` example deletes the tag with the specified key from the object ``doc1.rtf``. ::

    aws s3api delete-object-tagging \
        --bucket my-bucket \
        --key doc1.rtf

This command produces no output.