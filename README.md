Code based on happyhorseskull's.

Added two types of moshing:

- By removing all i-frames after the specified starting frame. This creates the glitchy transition effect.

- By repeating the first p-frame after the specified starting frame until the ending frame is reached.
This creates the melting effect. (`-d` flag specifies to use this method)
